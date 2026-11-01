import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.BulkRequest;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonData;
import co.elastic.clients.json.JsonpUtils;
import dev.esweb.travel.EsConfiguration;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.common.TopicPartition;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.databind.node.ObjectNode;

/** F45 bounded, single-partition lab; source writes are paused at acceptance. */
public class F45Lab {
    static final JsonMapper JSON = JsonMapper.builder().build();
    static final String TOPIC = "travel_f45.f45.projection_event";
    static final TopicPartition TP = new TopicPartition(TOPIC, 0);
    static final Path LOCAL = Path.of("labs/f45/.local");
    static void check(boolean ok, String why) { if (!ok) throw new IllegalStateException(why); }
    static void log(Object v) { System.out.println(JSON.writeValueAsString(v)); System.out.flush(); }
    static Properties properties() {
        var p = new Properties();
        p.put("bootstrap.servers", "127.0.0.1:29345");
        p.put("group.id", "f45-projection");
        p.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        p.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        p.put("enable.auto.commit", "false"); p.put("auto.offset.reset", "none");
        p.put("max.poll.records", "20"); p.put("default.api.timeout.ms", "15000");
        p.put("request.timeout.ms", "10000");
        return p;
    }
    static JsonNode positions() throws Exception {
        try (var a = Admin.create(properties()); var c = new KafkaConsumer<String,String>(properties())) {
            c.assign(List.of(TP));
            var d = a.describeTopics(List.of(TOPIC)).allTopicNames().get(15, TimeUnit.SECONDS).get(TOPIC);
            check(d.partitions().size() == 1, "Require one partition");
            var next = c.committed(Set.of(TP)).get(TP);
            return JSON.valueToTree(Map.of("topic_id", d.topicId().toString(),
                "begin", c.beginningOffsets(List.of(TP)).get(TP),
                "end", c.endOffsets(List.of(TP)).get(TP), "next", next == null ? -1 : next.offset()));
        }
    }
    static JsonNode envelope(String key, String value) {
        check(value != null, "Append-only outbox must not have tombstones");
        var e = JSON.readTree(value); var s = e.path("source"); var row = e.path("after");
        check(s.path("db").asString().equals("travel_f45") && s.path("schema").asString().equals("f45")
            && s.path("table").asString().equals("projection_event")
            && List.of("r", "c").contains(e.path("op").asString()), "Unexpected source/op");
        check(JSON.readTree(key).path("event_id").equals(row.path("event_id")), "Event key mismatch");
        return row;
    }
    static ObjectNode document(String raw) throws Exception {
        var d = (ObjectNode) JSON.readTree(raw);
        check(d.path("attraction_id").asString().matches("n0[1-8]")
            && d.path("sync_revision").asLong() > 0 && !d.has("sync_hash"), "Invalid full snapshot");
        d.put("sync_hash", HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256")
            .digest(raw.getBytes(StandardCharsets.UTF_8))));
        return d;
    }
    static void apply(ElasticsearchClient es, List<ObjectNode> docs) throws Exception {
        if (docs.isEmpty()) return;
        String script = Files.readString(Path.of("search/f45/guard.painless"));
        var bulk = new BulkRequest.Builder().requireAlias(true);
        for (var doc : docs) bulk.operations(o -> o.update(u -> u.index("tut-f45-attractions-write")
            .id(doc.path("attraction_id").asString()).retryOnConflict(3)
            .action(a -> a.script(s -> s.lang("painless").source(v -> v.scriptString(script))
                .params("document", JsonData.fromJson(JSON.writeValueAsString(doc))))
                .scriptedUpsert(true).upsert(JsonData.fromJson("{}")))));
        var reply = es.bulk(bulk.build());
        check(reply.items().size() == docs.size(), "Wrong item count");
        boolean failed = false;
        for (int i = 0; i < docs.size(); i++) {
            var item = reply.items().get(i);
            check(item.id().equals(docs.get(i).path("attraction_id").asString()), "Wrong item ID");
            log(Map.of("kind", "item", "id", item.id(), "status", item.status(),
                "result", item.result() == null ? "" : item.result(),
                "error", item.error() == null ? "" : item.error().toString()));
            failed |= item.error() != null || item.status() >= 300;
        }
        check(!failed, "Unresolved ES items; checkpoint not committed");
    }
    static void consume(ElasticsearchClient es, String mode, long high) throws Exception {
        try (var c = new KafkaConsumer<String,String>(properties())) {
            c.assign(List.of(TP));
            long begin = c.beginningOffsets(List.of(TP)).get(TP), end = c.endOffsets(List.of(TP)).get(TP);
            var saved = c.committed(Set.of(TP)).get(TP);
            if (mode.equals("seed")) {
                check(saved == null && high == begin && begin == 0, "Seed only a fresh group/topic");
                c.commitSync(Map.of(TP, new OffsetAndMetadata(high))); log(Map.of("kind", "seed", "next", high)); return;
            }
            long next = mode.equals("events") ? begin : saved == null ? -1 : saved.offset();
            check(begin <= next && next <= high && high <= end, "Outside retained/committed boundary");
            c.seek(TP, next); long deadline = System.nanoTime() + Duration.ofSeconds(45).toNanos();
            while (next < high) {
                var records = c.poll(Duration.ofMillis(200)).records(TP).stream().filter(r -> r.offset() < high).toList();
                if (!records.isEmpty()) {
                    var docs = new ArrayList<ObjectNode>();
                    for (var r : records) {
                        var row = envelope(r.key(), r.value());
                        var d = document(row.path("document").asString());
                        check(d.path("attraction_id").equals(row.path("attraction_id"))
                            && d.path("sync_revision").asLong() == row.path("revision").asLong(), "Revision/ID mismatch");
                        if (mode.equals("events")) log(Map.of("kind", "event", "offset", r.offset(), "key", r.key(), "value", r.value()));
                        else docs.add(d);
                    }
                    if (!mode.equals("events")) apply(es, docs);
                    next = records.getLast().offset() + 1;
                    // ES can succeed before this commit; the guard makes replay safe.
                    if (!mode.equals("events")) c.commitSync(Map.of(TP, new OffsetAndMetadata(next)));
                }
                check(System.nanoTime() < deadline, "Bounded consumer timed out");
            }
            log(Map.of("kind", mode, "next", next, "high", high));
        }
    }
    static void search(ElasticsearchClient es, String name) throws Exception {
        check(List.of("attractions", "hotels").contains(name), "Unknown search");
        String index = name.equals("hotels") ? "tut-f45-hotels" : "tut-f45-attractions-read";
        var request = new SearchRequest.Builder().index(index).allowPartialSearchResults(false)
            .withJson(new java.io.StringReader(Files.readString(Path.of("search/f45/" + name + ".json")))).build();
        var reply = es.search(request, JsonData.class);
        check(!reply.timedOut() && reply.shards().failed().intValue() == 0, "Incomplete search");
        log(Map.of("kind", "search", "request", JSON.readTree(JsonpUtils.toJsonString(request, es._jsonpMapper())),
            "reply", JSON.readTree(JsonpUtils.toJsonString(reply, es._jsonpMapper()))));
    }
    public static void main(String[] args) throws Exception {
        if (args[0].equals("inspect")) { log(positions()); return; }
        Files.createDirectories(LOCAL);
        try (var channel = FileChannel.open(LOCAL.resolve("worker.lock"), StandardOpenOption.CREATE, StandardOpenOption.WRITE);
             var lock = channel.tryLock(); var es = EsConfiguration.connect("http://127.0.0.1:20945", "", "")) {
            check(lock != null, "Another local F45 worker is running");
            switch (args[0]) {
                case "seed", "drain", "events" -> consume(es, args[0], Long.parseLong(args[1]));
                case "search" -> search(es, args[1]);
                case "replay" -> {
                    var docs = new ArrayList<ObjectNode>();
                    for (var raw : JSON.readTree(Files.readString(Path.of(args[1])))) docs.add(document(raw.asString()));
                    apply(es, docs);
                }
                default -> throw new IllegalArgumentException("inspect | seed/drain/events H | search attractions/hotels | replay FILE");
            }
        }
    }
}
