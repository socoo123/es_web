import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.BulkRequest;
import co.elastic.clients.json.JsonData;
import dev.esweb.travel.EsConfiguration;
import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.common.TopicPartition;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.databind.node.ObjectNode;

/** F41: two independent target checkpoints, one immutable source partition. */
public class F41Worker {
    static final String TOPIC="travel_f41.f41.projection_event";
    static final TopicPartition TP=new TopicPartition(TOPIC,0);
    static final JsonMapper JSON=JsonMapper.builder().build();
    static final Path LOCK=Path.of("labs/f41/.local/worker.lock");
    static final String SCRIPT=read("search/f41/guard.painless");
    record Document(String id,long revision,JsonData body) {}

    static String read(String file) {
        try { return Files.readString(Path.of(file)); }
        catch(IOException e) { throw new IllegalStateException(e); }
    }
    static void log(Object value) { System.out.println(JSON.writeValueAsString(value));System.out.flush(); }
    static void check(boolean ok,String message) { if(!ok) throw new IllegalStateException(message); }
    static String group(String version) { return "f41-"+version; }
    static String writer(String version) { return "tut-f41-"+version+"-ingest"; }
    static Properties properties(String version) {
        var p=new Properties();
        p.put("bootstrap.servers","127.0.0.1:29341");p.put("group.id",group(version));
        p.put("key.deserializer","org.apache.kafka.common.serialization.StringDeserializer");
        p.put("value.deserializer","org.apache.kafka.common.serialization.StringDeserializer");
        p.put("enable.auto.commit","false");p.put("auto.offset.reset","none");
        p.put("max.poll.records","10");p.put("session.timeout.ms","6000");
        p.put("heartbeat.interval.ms","2000");p.put("default.api.timeout.ms","20000");
        p.put("request.timeout.ms","10000");
        return p;
    }
    static Document project(String raw,String version) throws Exception {
        ObjectNode doc=(ObjectNode)JSON.readTree(raw);
        String id=doc.path("attraction_id").asString("");
        long revision=doc.path("sync_revision").asLong(-1);
        check(id.matches("p[0-9]{2}") && revision>0 && doc.path("sync_deleted").isBoolean(),"Invalid canonical projection");
        check(!doc.has("sync_hash") && !doc.has("projection_schema") && !doc.has("price_band"),"Require canonical source fields");
        int schema=version.equals("v1")?1:2;
        if(schema==2 && !doc.path("sync_deleted").asBoolean()) {
            check(doc.path("ticket_price_fen").isIntegralNumber(),"Price must be integer fen");
            long price=doc.path("ticket_price_fen").asLong();check(price>=0,"Negative price");
            doc.put("price_band",price==0?"free":price<5000?"under_50":"from_50");
        }
        doc.put("projection_schema",schema);
        // Same SQL JSONB text for the full snapshot and immutable outbox.
        // Projection schema is part of the fingerprint; never share a guard
        // state between v1 and v2, or relabel an old payload with a new revision.
        String hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256")
            .digest((schema+"\n"+raw).getBytes(StandardCharsets.UTF_8)));
        doc.put("sync_hash",hash);
        return new Document(id,revision,JsonData.fromJson(JSON.writeValueAsString(doc)));
    }
    static JsonNode envelope(ConsumerRecord<String,String> record) throws Exception {
        check(record.topic().equals(TOPIC) && record.partition()==0 && record.value()!=null,"Unexpected source");
        JsonNode e=JSON.readTree(record.value()),s=e.path("source"),a=e.path("after");
        check(s.path("db").asString("").equals("travel_f41") && s.path("schema").asString("").equals("f41")
            && s.path("table").asString("").equals("projection_event") && List.of("r","c").contains(e.path("op").asString("")),"Require append-only outbox r/c");
        check(JSON.readTree(record.key()).path("event_id").equals(a.path("event_id")),"Outbox key mismatch");
        check(List.of("document","fence").contains(a.path("kind").asString("")),"Unknown event kind");
        return a;
    }
    static void apply(ElasticsearchClient es,String version,List<Document> documents) throws Exception {
        if(documents.isEmpty())return;
        var bulk=new BulkRequest.Builder().requireAlias(true);
        for(var doc:documents) bulk.operations(o->o.update(u->u.index(writer(version)).id(doc.id()).retryOnConflict(3)
            .action(a->a.script(s->s.lang("painless").source(v->v.scriptString(SCRIPT))
                .params("revision",JsonData.of(doc.revision())).params("document",doc.body()))
                .scriptedUpsert(true).upsert(JsonData.fromJson("{}")))));
        var response=es.bulk(bulk.build());check(response.items().size()==documents.size(),"Bulk item count mismatch");
        var failures=new ArrayList<String>();
        for(int i=0;i<documents.size();i++) {
            var doc=documents.get(i);var item=response.items().get(i);
            check(doc.id().equals(item.id()),"Bulk ID mismatch");
            log(Map.of("kind","item","target",version,"index",item.index(),"id",doc.id(),"revision",doc.revision(),
                "status",item.status(),"result",item.result()==null?"":item.result(),"error",item.error()==null?"":item.error().toString()));
            if(item.error()!=null || item.status()>=300) failures.add(doc.id()+":"+item.status());
        }
        // No DLQ waiver in a rebuild gate. Recovery replays uncommitted work
        // through the same guard; F40's transient retry policy can be added.
        check(failures.isEmpty(),"Unresolved target items; no checkpoint commit: "+failures);
    }
    static void inspect() throws Exception {
        try(var admin=Admin.create(properties("inspect"));var consumer=new KafkaConsumer<String,String>(properties("inspect"))) {
            var description=admin.describeTopics(List.of(TOPIC)).allTopicNames().get(20,TimeUnit.SECONDS).get(TOPIC);
            check(description.partitions().size()==1,"Require exactly one source partition");
            consumer.assign(List.of(TP));var begin=consumer.beginningOffsets(List.of(TP)).get(TP);var end=consumer.endOffsets(List.of(TP)).get(TP);
            var groups=new LinkedHashMap<String,Object>();
            for(var version:List.of("v1","v2")) {
                var offsets=admin.listConsumerGroupOffsets(group(version)).partitionsToOffsetAndMetadata().get(20,TimeUnit.SECONDS);
                var offset=offsets.get(TP);groups.put(version,offset==null?-1:offset.offset());
            }
            log(Map.of("kind","positions","topic",TOPIC,"partition",0,"topic_id",description.topicId().toString(),
                "kafka_cluster_id",admin.describeCluster().clusterId().get(20,TimeUnit.SECONDS),"begin",begin,"end",end,"committed_next",groups));
        }
    }
    static void events() throws Exception {
        try(var c=new KafkaConsumer<String,String>(properties("inspect"))) {
            c.assign(List.of(TP));c.seekToBeginning(List.of(TP));long end=c.endOffsets(List.of(TP)).get(TP);
            long deadline=System.nanoTime()+Duration.ofSeconds(40).toNanos();
            while(c.position(TP)<end) {
                for(var r:c.poll(Duration.ofMillis(200))) if(r.offset()<end) {
                    envelope(r);
                    log(Map.of("kind","event","offset",r.offset(),"key",r.key(),"value",r.value()));
                }
                check(System.nanoTime()<deadline,"Event inspection timed out");
            }
            log(Map.of("kind","events_end","end",end));
        }
    }
    static void seed(String version,long next) {
        try(var c=new KafkaConsumer<String,String>(properties(version))) {
            c.assign(List.of(TP));long begin=c.beginningOffsets(List.of(TP)).get(TP),end=c.endOffsets(List.of(TP)).get(TP);
            check(c.committed(Set.of(TP)).get(TP)==null,"Refuse to reset an existing target checkpoint");
            check(next>=begin && next<=end,"Seed outside retained source");
            c.commitSync(Map.of(TP,new OffsetAndMetadata(next,"f41-explicit-start")));
            log(Map.of("kind","seed","target",version,"next",next));
        }
    }
    static void drain(ElasticsearchClient es,String version,long high) throws Exception {
        try(var c=new KafkaConsumer<String,String>(properties(version))) {
            c.subscribe(List.of(TOPIC));long deadline=System.nanoTime()+Duration.ofSeconds(80).toNanos();
            while(c.assignment().isEmpty()) { c.poll(Duration.ofMillis(200));check(System.nanoTime()<deadline,"Consumer join timed out"); }
            check(c.assignment().equals(Set.of(TP)),"Only one worker per target, one partition required");
            var offset=c.committed(Set.of(TP)).get(TP);check(offset!=null,"Explicit target seed required");
            long next=offset.offset(),begin=c.beginningOffsets(List.of(TP)).get(TP),end=c.endOffsets(List.of(TP)).get(TP);
            check(next>=begin && next<=high && high<=end,"Checkpoint outside retained source or requested fence");c.seek(TP,next);
            long processed=0;
            while(next<high) {
                var records=c.poll(Duration.ofMillis(200)).records(TP).stream().filter(r->r.offset()<high).toList();
                if(!records.isEmpty()) {
                    var documents=new ArrayList<Document>();
                    for(var r:records) {
                        var after=envelope(r);
                        if(after.path("kind").asString().equals("fence")) {
                            check(!after.path("fence_key").asString("").isBlank(),"Missing fence key");
                            log(Map.of("kind","fence","key",after.path("fence_key").asString(),"offset",r.offset()));
                        } else {
                            var doc=project(after.path("document").asString(),version);
                            check(doc.id().equals(after.path("attraction_id").asString()) && doc.revision()==after.path("revision").asLong(),"Source revision mismatch");
                            documents.add(doc);
                        }
                    }
                    apply(es,version,documents);
                    var last=records.getLast();next=last.offset()+1;
                    c.commitSync(Map.of(TP,new OffsetAndMetadata(next,last.leaderEpoch(),"f41-applied-through-fence")));
                    log(Map.of("kind","commit","target",version,"next",next));processed+=records.size();
                }
                check(System.nanoTime()<deadline,"Bounded drain timed out");
            }
            log(Map.of("kind","drained","target",version,"next",next,"high",high,"processed",processed));
        }
    }
    public static void main(String[] args) throws Exception {
        check(args.length>=1,"inspect | events | seed version next | drain version high | snapshot version file");
        String mode=args[0];
        if(mode.equals("inspect")){inspect();return;}if(mode.equals("events")){events();return;}
        check(args.length==3 && List.of("v1","v2").contains(args[1]),"Target and boundary/file required");
        check(List.of("seed","drain","snapshot").contains(mode),"Unknown mode");String version=args[1];
        Files.createDirectories(LOCK.getParent());
        try(var channel=FileChannel.open(LOCK,StandardOpenOption.CREATE,StandardOpenOption.WRITE);var lock=channel.tryLock()) {
            check(lock!=null,"Another F41 worker or alias coordinator is active");
            if(mode.equals("seed")){seed(version,Long.parseLong(args[2]));return;}
            try(var es=EsConfiguration.connect("http://127.0.0.1:20541","","")) {
                if(mode.equals("drain"))drain(es,version,Long.parseLong(args[2]));
                else {
                    var snapshot=JSON.readTree(read(args[2]));var documents=new ArrayList<Document>();
                    check(snapshot.path("documents").isArray(),"Snapshot document array required");
                    for(var raw:snapshot.path("documents"))documents.add(project(raw.asString(),version));
                    apply(es,version,documents);
                    log(Map.of("kind","snapshot_applied","target",version,"documents",documents.size(),"kafka_checkpoint_changed",false));
                }
            }
        }
    }
}
