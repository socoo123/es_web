import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.ElasticsearchException;
import co.elastic.clients.elasticsearch.core.BulkRequest;
import co.elastic.clients.json.JsonData;
import dev.esweb.travel.EsConfiguration;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.TopicPartition;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** F40: one consumer, per-partition batches, immutable complete projection events. */
public class F40Consumer {
    static final String PREFIX="travel_f40.f40.", GROUP="f40-es-v1", DLQ="f40-es-dlq";
    static final String WRITE="tut-f40-attractions-write";
    static final List<String> CHANNELS=List.of("root", "related");
    static final JsonMapper JSON=JsonMapper.builder().build();
    static final int ATTEMPTS=4;
    static final String SCRIPT=read("search/f40/guard.painless");
    record Event(ConsumerRecord<String,String> record, String id, long revision, JsonData document) {}

    static String read(String file) {
        try { return Files.readString(Path.of(file)); }
        catch(IOException e) { throw new IllegalStateException(e); }
    }
    static void log(Object value) { System.out.println(JSON.writeValueAsString(value)); System.out.flush(); }
    static Properties properties() {
        var p=new Properties();
        p.put("bootstrap.servers", "127.0.0.1:29340");
        p.put("group.id", GROUP);
        p.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        p.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        p.put("enable.auto.commit", "false");
        p.put("auto.offset.reset", "earliest");
        p.put("max.poll.records", "10");
        p.put("session.timeout.ms", "6000");
        p.put("heartbeat.interval.ms", "2000");
        p.put("default.api.timeout.ms", "20000");
        return p;
    }
    static KafkaProducer<String,String> producer() {
        var p=new Properties();
        p.put("bootstrap.servers", "127.0.0.1:29340");
        p.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        p.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        p.put("acks", "all"); p.put("enable.idempotence", "true");
        p.put("request.timeout.ms", "5000"); p.put("delivery.timeout.ms", "15000");
        p.put("max.block.ms", "10000");
        return new KafkaProducer<>(p);
    }
    static String field(JsonNode n,String key) {
        String value=n.path(key).asString("");
        if(value.isBlank()) throw new IllegalArgumentException("Missing "+key);
        return value;
    }
    static Event parse(ConsumerRecord<String,String> r) throws Exception {
        if(!CHANNELS.stream().map(c->PREFIX+c+"_event").toList().contains(r.topic()))
            throw new IllegalArgumentException("Unexpected source topic");
        if(r.value()==null) throw new IllegalArgumentException("Append-only outbox must not be deleted");
        JsonNode envelope=JSON.readTree(r.value()), source=envelope.path("source");
        if(!"travel_f40".equals(source.path("db").asString()) || !"f40".equals(source.path("schema").asString())
            || !r.topic().equals(PREFIX+source.path("table").asString())
            || !List.of("r","c").contains(envelope.path("op").asString()))
            throw new IllegalArgumentException("Require immutable outbox r/c event");
        JsonNode after=envelope.path("after");
        if(!JSON.readTree(r.key()).path("event_id").equals(after.path("event_id")))
            throw new IllegalArgumentException("Outbox key mismatch");
        String id=field(after,"attraction_id"); long revision=after.path("revision").asLong(-1);
        String raw=field(after,"document");
        var document=JSON.readTree(raw);
        if(!id.matches("p[0-9]{2}") || revision<=0 || !id.equals(document.path("attraction_id").asString())
            || revision!=document.path("sync_revision").asLong(-1)
            || !after.path("deleted").isBoolean() || !document.path("sync_deleted").isBoolean()
            || after.path("deleted").asBoolean()!=document.path("sync_deleted").asBoolean()
            || document.has("sync_hash")) throw new IllegalArgumentException("Invalid projection envelope");
        // The immutable source's exact JSONB serialization is stable on replay.
        String hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(raw.getBytes(StandardCharsets.UTF_8)));
        var body=(tools.jackson.databind.node.ObjectNode)document;
        body.put("sync_hash",hash);
        return new Event(r,id,revision,JsonData.fromJson(JSON.writeValueAsString(body)));
    }
    static Map<String,Object> origin(ConsumerRecord<String,String> r) {
        return Map.of("topic",r.topic(),"partition",r.partition(),"offset",r.offset());
    }
    static void park(KafkaProducer<String,String> producer,ConsumerRecord<String,String> r,String reason) throws Exception {
        String key=r.topic()+":"+r.partition()+":"+r.offset();
        var value=new LinkedHashMap<String,Object>();
        value.put("origin",origin(r)); value.put("key",r.key()); value.put("value",r.value());
        value.put("reason",reason); value.put("resolution","pending");
        var ack=producer.send(new ProducerRecord<>(DLQ,key,JSON.writeValueAsString(value))).get();
        log(Map.of("kind","parked","origin",origin(r),"dlq_key",key,"dlq_partition",ack.partition(),"dlq_offset",ack.offset()));
    }
    static boolean transientStatus(int status) { return List.of(409,429,502,503,504).contains(status); }
    static void backoff(int attempt) throws InterruptedException {
        long ms=Math.min(1600,200L<<(attempt-1))+ThreadLocalRandom.current().nextLong(151);
        log(Map.of("kind","backoff","attempt",attempt,"milliseconds",ms)); Thread.sleep(ms);
    }
    static void apply(ElasticsearchClient es,KafkaProducer<String,String> producer,
                      List<ConsumerRecord<String,String>> records,boolean allowPark) throws Exception {
        var pending=new ArrayList<Event>();
        for(var r:records) {
            try { pending.add(parse(r)); }
            catch(IllegalArgumentException e) {
                if(!allowPark) throw e;
                park(producer,r,"validation: "+e.getMessage());
            }
        }
        for(int attempt=1;!pending.isEmpty() && attempt<=ATTEMPTS;attempt++) {
            var bulk=new BulkRequest.Builder().requireAlias(true);
            for(var event:pending) bulk.operations(o->o.update(u->u.index(WRITE).id(event.id()).retryOnConflict(3)
                .action(a->a.script(s->s.lang("painless").source(v->v.scriptString(SCRIPT))
                    .params("revision",JsonData.of(event.revision())).params("document",event.document()))
                    .scriptedUpsert(true).upsert(JsonData.fromJson("{}")))));
            var retry=new ArrayList<Event>(); var blocked=new ArrayList<String>();
            try {
                var response=es.bulk(bulk.build());
                if(response.items().size()!=pending.size()) throw new IllegalStateException("Bulk item count mismatch");
                for(int i=0;i<pending.size();i++) {
                    var event=pending.get(i); var item=response.items().get(i);
                    if(!event.id().equals(item.id())) throw new IllegalStateException("Bulk item ID mismatch");
                    String reason=item.error()==null ? "" : item.error().toString();
                    log(Map.of("kind","item","origin",origin(event.record()),"id",event.id(),"revision",event.revision(),
                        "attempt",attempt,"status",item.status(),"result",item.result()==null?"":item.result(),"error",reason));
                    if(item.error()==null && item.status()<300) continue;
                    if(transientStatus(item.status())) retry.add(event);
                    else if(item.status()==400 && allowPark && item.error()!=null
                        && List.of("document_parsing_exception","mapper_parsing_exception").contains(item.error().type()))
                        park(producer,event.record(),reason);
                    else blocked.add(event.id()+" status="+item.status());
                }
            } catch(ElasticsearchException e) {
                if(!transientStatus(e.status())) throw e;
                retry.addAll(pending); log(Map.of("kind","request_retry","attempt",attempt,"status",e.status()));
            } catch(IOException e) {
                // The request might have been applied before its acknowledgement was lost.
                retry.addAll(pending); log(Map.of("kind","request_retry","attempt",attempt,"status","io_unknown_outcome"));
            }
            if(!blocked.isEmpty()) throw new IllegalStateException("Unresolved items; no batch commit: "+blocked);
            pending=retry;
            if(!pending.isEmpty()) {
                if(attempt==ATTEMPTS) throw new IllegalStateException("Retry budget exhausted; no batch commit");
                backoff(attempt);
            }
        }
    }
    public static void main(String[] args) throws Exception {
        if(args.length<1) throw new IllegalArgumentException("inspect | dlq | drain channel [block|park|crash] | replay channel | repair file");
        String mode=args[0],channel=args.length>1?args[1]:"all",policy=args.length>2?args[2]:"block";
        if(!List.of("inspect","dlq","drain","replay","repair").contains(mode)
            || !List.of("block","park","crash").contains(policy)) throw new IllegalArgumentException("Invalid mode/policy");
        String endpoint=System.getenv().getOrDefault("F40_ES_URL","http://127.0.0.1:20440");
        if(!List.of("http://127.0.0.1:20440","http://127.0.0.1:20441").contains(endpoint))
            throw new IllegalArgumentException("Use the isolated F40 ES or fault proxy");
        boolean inspect=mode.equals("inspect")||mode.equals("dlq"),replay=mode.equals("replay"),repair=mode.equals("repair");
        try(var es=inspect?null:EsConfiguration.connect(endpoint,"",""); var producer=inspect?null:producer()) {
            if(repair) {
                JsonNode audit=JSON.readTree(read(channel)); JsonNode src=audit.path("origin");
                var record=new ConsumerRecord<String,String>(field(src,"topic"),src.path("partition").asInt(),src.path("offset").asLong(),field(audit,"key"),field(audit,"value"));
                if(!audit.has("repair_note") || field(audit,"repair_note").isBlank()) throw new IllegalArgumentException("Reviewed repair note required");
                apply(es,producer,List.of(record),false);
                log(Map.of("kind","repaired","origin",origin(record),"source_offsets_changed",false,"note",field(audit,"repair_note")));return;
            }
            if(!List.of("all","root","related").contains(channel)) throw new IllegalArgumentException("Channel required");
            var topics=mode.equals("dlq")?List.of(DLQ):CHANNELS.stream().filter(c->channel.equals("all")||channel.equals(c)).map(c->PREFIX+c+"_event").toList();
            var partitions=topics.stream().map(t->new TopicPartition(t,0)).toList();
            try(var consumer=new KafkaConsumer<String,String>(properties())) {
                for(var t:topics) if(consumer.partitionsFor(t).size()!=1) throw new IllegalStateException("Require one partition per topic");
                if(inspect||replay) { consumer.assign(partitions);consumer.seekToBeginning(partitions); }
                else {
                    consumer.subscribe(topics); long join=System.nanoTime()+Duration.ofSeconds(40).toNanos();
                    while(consumer.assignment().isEmpty()) { consumer.poll(Duration.ofMillis(200));if(System.nanoTime()>join)throw new IllegalStateException("Join timeout"); }
                    if(!consumer.assignment().equals(Set.copyOf(partitions))) throw new IllegalStateException("Only one F40 consumer allowed");
                    var committed=consumer.committed(Set.copyOf(partitions));
                    for(var tp:partitions) {
                        if(committed.get(tp)==null) consumer.seekToBeginning(List.of(tp));else consumer.seek(tp,committed.get(tp).offset());
                    }
                }
                var ends=consumer.endOffsets(partitions);long processed=0,deadline=System.nanoTime()+Duration.ofSeconds(80).toNanos();
                while(partitions.stream().anyMatch(tp->consumer.position(tp)<ends.get(tp))) {
                    var polled=consumer.poll(Duration.ofMillis(300));
                    for(var tp:partitions) {
                        var records=polled.records(tp).stream().filter(r->r.offset()<ends.get(tp)).toList();
                        if(records.isEmpty())continue;
                        if(inspect) for(var r:records) {
                            var entry=new LinkedHashMap<String,Object>();entry.put("kind","event");entry.put("origin",origin(r));
                            entry.put("key",r.key());entry.put("value",r.value());log(entry);
                        } else {
                            apply(es,producer,records,policy.equals("park"));
                            if(policy.equals("crash")) {
                                log(Map.of("kind","crash_window","written",records.size(),"committed",false));
                                Runtime.getRuntime().halt(40); // Intentional abrupt exit after ES, before Kafka commit.
                            }
                            if(!replay) {
                                var last=records.getLast();long next=last.offset()+1;
                                consumer.commitSync(Map.of(tp,new OffsetAndMetadata(next,last.leaderEpoch(),"f40-resolved-batch")));
                                log(Map.of("kind","commit","topic",tp.topic(),"partition",tp.partition(),"next",next));
                            }
                        }
                        processed+=records.size();
                    }
                    if(System.nanoTime()>deadline)throw new IllegalStateException("Drain timeout");
                }
                var positions=new LinkedHashMap<String,Object>();var committed=consumer.committed(Set.copyOf(partitions));
                for(var tp:partitions) positions.put(tp.topic(),Map.of("observed_end",ends.get(tp),"committed_next",committed.get(tp)==null?-1:committed.get(tp).offset()));
                log(Map.of("kind","summary","mode",mode,"processed",processed,"positions",positions));
            }
        }
    }
}
