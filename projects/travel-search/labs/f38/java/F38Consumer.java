import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.json.JsonData;
import dev.esweb.travel.EsConfiguration;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.common.TopicPartition;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** One topic, one partition, one consumer, immutable primary key. F40 adds failure/replay design. */
public class F38Consumer {
    static final String TOPIC = "travel_f38.travel_f38.attraction";
    static final String GROUP = "f38-es-v1";
    static final String WRITE = "tut-f38-attractions-write";
    static final JsonMapper JSON = JsonMapper.builder().build();

    static Properties properties() {
        var p = new Properties();
        p.put("bootstrap.servers", "127.0.0.1:29238");
        p.put("group.id", GROUP);
        p.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        p.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        p.put("enable.auto.commit", "false");
        p.put("auto.offset.reset", "earliest");
        p.put("max.poll.records", "10");
        p.put("default.api.timeout.ms", "20000");
        return p;
    }

    static String apply(ElasticsearchClient es, ConsumerRecord<String, String> record) throws Exception {
        JsonNode key = JSON.readTree(record.key());
        String id = key.path("attraction_id").asString();
        if (!id.matches("p[0-9]{2}")) throw new IllegalArgumentException("Invalid business key");
        // Debezium's d event performed the deletion; a null Kafka value is a compaction marker.
        if (record.value() == null) return "tombstone";
        JsonNode event = JSON.readTree(record.value());
        JsonNode source = event.path("source");
        if (!"travel_f38".equals(source.path("db").asString())
                || !"attraction".equals(source.path("table").asString())) {
            throw new IllegalArgumentException("Unexpected event source");
        }
        String op = event.path("op").asString();
        if ("d".equals(op)) {
            if (!event.path("after").isNull()
                    || !id.equals(event.path("before").path("attraction_id").asString())) {
                throw new IllegalArgumentException("Delete key/shape mismatch");
            }
            // A missing document is an acceptable result for this key-based delete.
            return "delete:" + es.delete(d -> d.index(WRITE).id(id)).result().jsonValue();
        }
        if (!List.of("r", "c", "u").contains(op)) throw new IllegalArgumentException("Unsupported operation");
        JsonNode after = event.path("after");
        if (!id.equals(after.path("attraction_id").asString())) {
            throw new IllegalArgumentException("Key/after mismatch; primary key changes are out of scope");
        }
        String status = after.path("status").asString();
        if ("closed".equals(status)) {
            return "delete:" + es.delete(d -> d.index(WRITE).id(id)).result().jsonValue();
        }
        if (!"open".equals(status)) throw new IllegalArgumentException("Unknown status");
        var document = Map.of(
            "attraction_id", id, "name", after.path("name").asString(),
            "city_code", after.path("city_code").asString(),
            "ticket_price_fen", after.path("ticket_price_fen").asLong(),
            "currency", "CNY", "status", status,
            "location", Map.of("lat", after.path("latitude").asDouble(),
                               "lon", after.path("longitude").asDouble()));
        var body = JsonData.fromJson(JSON.writeValueAsString(document));
        return "index:" + es.index(i -> i.index(WRITE).requireAlias(true).id(id).document(body)).result().jsonValue();
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 1 || !List.of("inspect", "drain", "follow").contains(args[0])) {
            throw new IllegalArgumentException("inspect | drain | follow required");
        }
        boolean inspect = args[0].equals("inspect"), follow = args[0].equals("follow");
        var tp = new TopicPartition(TOPIC, 0);
        try (var consumer = new KafkaConsumer<String, String>(properties());
             var es = inspect ? null : EsConfiguration.connect("http://127.0.0.1:20238", "", "")) {
            if (consumer.partitionsFor(TOPIC).size() != 1) {
                throw new IllegalStateException("This lab requires exactly one partition");
            }
            if (inspect) {
                consumer.assign(List.of(tp));
                consumer.seekToBeginning(List.of(tp));
            } else {
                consumer.subscribe(List.of(TOPIC));
                // poll can fetch records while joining: rewind to the committed position before processing.
                long deadline = System.nanoTime() + Duration.ofSeconds(30).toNanos();
                while (consumer.assignment().isEmpty()) {
                    consumer.poll(Duration.ofMillis(200));
                    if (System.nanoTime() > deadline) throw new IllegalStateException("Assignment timed out");
                }
                if (!consumer.assignment().equals(java.util.Set.of(tp))) {
                    throw new IllegalStateException("Use only one F38 consumer");
                }
                var committed = consumer.committed(java.util.Set.of(tp)).get(tp);
                if (committed == null) consumer.seekToBeginning(List.of(tp));
                else consumer.seek(tp, committed.offset());
            }
            // For drain/inspect, writes must be paused: this is a finite observation boundary, not a global checkpoint.
            long end = consumer.endOffsets(List.of(tp)).get(tp);
            long processed = 0, deadline = System.nanoTime() + Duration.ofSeconds(60).toNanos();
            while (follow || consumer.position(tp) < end) {
                var records = consumer.poll(Duration.ofMillis(500));
                for (var record : records) {
                    if (!inspect) {
                        String result = apply(es, record); // an exception exits before committing this record
                        consumer.commitSync(Map.of(tp, new OffsetAndMetadata(record.offset() + 1)));
                        System.out.println(JSON.writeValueAsString(Map.of("kind", "applied",
                            "partition", record.partition(), "offset", record.offset(),
                            "key", JSON.readTree(record.key()), "result", result,
                            "committed_next", record.offset() + 1)));
                    } else {
                        var output = JSON.createObjectNode();
                        output.put("kind", "event").put("partition", record.partition()).put("offset", record.offset());
                        output.set("key", JSON.readTree(record.key()));
                        output.set("value", record.value() == null ? JSON.nullNode() : JSON.readTree(record.value()));
                        System.out.println(JSON.writeValueAsString(output));
                    }
                    processed++;
                }
                if (!follow && System.nanoTime() > deadline) throw new IllegalStateException("Drain timed out");
            }
            var committed = inspect ? null : consumer.committed(java.util.Set.of(tp)).get(tp);
            System.out.println(JSON.writeValueAsString(Map.of("kind", "summary", "mode", args[0],
                "processed", processed, "observed_end", end,
                "committed_next", committed == null ? -1 : committed.offset())));
        }
    }
}
