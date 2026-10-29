import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.BulkRequest;
import co.elastic.clients.json.JsonData;
import dev.esweb.travel.EsConfiguration;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.TreeSet;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.common.TopicPartition;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Current-state recomputation from a primary DB, one consumer, stable row keys. */
public class F39Consumer {
    static final List<String> TABLES = List.of("city", "attraction", "attraction_tag");
    static final String PREFIX = "travel_f39.f39.";
    static final String GROUP = "f39-es-v1", WRITE = "tut-f39-attractions-write";
    static final JsonMapper JSON = JsonMapper.builder().build();
    static final String PROJECTION = """
        SELECT jsonb_build_object(
          'attraction_id',a.attraction_id,'name',a.name,
          'city_code',a.city_code,'city_name',c.city_name,
          'ticket_price_fen',a.ticket_price_fen,'currency','CNY','status',a.status,
          'location',jsonb_build_object('lat',a.latitude,'lon',a.longitude),
          'tags',COALESCE((SELECT jsonb_agg(t.tag ORDER BY t.tag COLLATE "C")
                          FROM f39.attraction_tag t WHERE t.attraction_id=a.attraction_id),'[]'::jsonb))
        FROM f39.attraction a JOIN f39.city c USING(city_code)
        WHERE a.attraction_id=? AND a.status='open'
        """;

    static Properties properties() {
        var p = new Properties();
        p.put("bootstrap.servers", "127.0.0.1:29339");
        p.put("group.id", GROUP);
        p.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        p.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        p.put("enable.auto.commit", "false");
        p.put("auto.offset.reset", "earliest");
        p.put("max.poll.records", "10");
        p.put("default.api.timeout.ms", "20000");
        return p;
    }

    static Connection database() throws Exception {
        var p = new Properties();
        try (var input = Files.newInputStream(Path.of("infra/f39/.local/projector.properties"))) {
            p.load(input);
        }
        String url = (String) p.remove("url");
        var db = DriverManager.getConnection(url, p); // Password is a property, never in URL or logs.
        db.setReadOnly(true);
        db.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);
        db.setAutoCommit(false);
        return db;
    }

    static String field(JsonNode node, String name) {
        String value = node.path(name).asString("");
        if (value.isBlank()) throw new IllegalArgumentException("Missing " + name + "; require FULL old row");
        return value;
    }

    static void id(Set<String> ids, JsonNode row) {
        String value = field(row, "attraction_id");
        if (!value.matches("p[0-9]{2}")) throw new IllegalArgumentException("Invalid attraction_id");
        ids.add(value);
    }

    static Set<String> affected(Connection db, ConsumerRecord<String, String> record) throws Exception {
        var ids = new TreeSet<String>();
        String table = record.topic().substring(PREFIX.length());
        if (!TABLES.contains(table)) throw new IllegalArgumentException("Unexpected topic");
        JsonNode key = JSON.readTree(record.key());
        String keyField = switch (table) {
            case "city" -> "city_code";
            case "attraction" -> "attraction_id";
            default -> "tag_id";
        };
        String rowKey = field(key, keyField);
        if (record.value() == null) return ids; // The d event routed deletion; null is a compaction marker.
        JsonNode event = JSON.readTree(record.value()), source = event.path("source");
        if (!"travel_f39".equals(source.path("db").asString())
                || !"f39".equals(source.path("schema").asString())
                || !table.equals(source.path("table").asString())) {
            throw new IllegalArgumentException("Unexpected source");
        }
        String op = field(event, "op");
        if (!List.of("r", "c", "u", "d").contains(op)) throw new IllegalArgumentException("Unsupported op");
        JsonNode before = event.path("before"), after = event.path("after");
        var rows = new ArrayList<JsonNode>();
        if (List.of("u", "d").contains(op)) rows.add(before);
        if (!"d".equals(op)) rows.add(after);
        for (JsonNode row : rows) {
            if (!rowKey.equals(field(row, keyField))) throw new IllegalArgumentException("Row key changed/mismatch");
            if (table.equals("city")) {
                try (var query = db.prepareStatement("SELECT attraction_id FROM f39.attraction WHERE city_code=? ORDER BY attraction_id")) {
                    query.setString(1, field(row, "city_code"));
                    try (var rs = query.executeQuery()) { while (rs.next()) ids.add(rs.getString(1)); }
                }
            } else {
                // A moved tag must invalidate both before.attraction_id and after.attraction_id.
                id(ids, row);
            }
        }
        return ids;
    }

    static Map<String, Object> apply(Connection db, ElasticsearchClient es,
            ConsumerRecord<String, String> record) throws Exception {
        var ids = affected(db, record);
        var operations = new ArrayList<Map<String, Object>>();
        var ndjson = new StringBuilder();
        var bulk = new BulkRequest.Builder().requireAlias(true);
        for (String id : ids) {
            String document = null;
            try (var query = db.prepareStatement(PROJECTION)) {
                query.setString(1, id);
                try (var rs = query.executeQuery()) { if (rs.next()) document = rs.getString(1); }
            }
            // Recompute every field. Missing/closed root deletes; an empty child set is explicitly [].
            String action = document == null ? "delete" : "index";
            ndjson.append(JSON.writeValueAsString(Map.of(action, Map.of("_index", WRITE, "_id", id)))).append('\n');
            if (document == null) {
                bulk.operations(o -> o.delete(d -> d.index(WRITE).id(id)));
                operations.add(Map.of("id", id, "op", "delete"));
            } else {
                var body = JsonData.fromJson(document);
                bulk.operations(o -> o.index(i -> i.index(WRITE).id(id).document(body)));
                ndjson.append(document).append('\n');
                operations.add(Map.of("id", id, "op", "index", "document", JSON.readTree(document)));
            }
        }
        // End this event's read-only snapshot. This does not form a transaction with ES/Kafka.
        db.commit();
        var results = new ArrayList<Map<String, Object>>();
        if (!ids.isEmpty()) {
            var response = es.bulk(bulk.build());
            if (response.items().size() != operations.size()) throw new IllegalStateException("Bulk item count");
            for (int i = 0; i < response.items().size(); i++) {
                var item = response.items().get(i);
                boolean missingDelete = operations.get(i).get("op").equals("delete") && item.status() == 404;
                if (item.error() != null || (item.status() >= 300 && !missingDelete)) {
                    throw new IllegalStateException("Bulk item failed: " + item.id() + " status=" + item.status());
                }
                results.add(Map.of("id", item.id(), "status", item.status(), "result", item.result()));
            }
        }
        return Map.of("affected_ids", ids, "operations", operations, "bulk_ndjson", ndjson.toString(), "items", results);
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 1 || !List.of("inspect", "drain", "follow").contains(args[0])) {
            throw new IllegalArgumentException("inspect | drain | follow required");
        }
        boolean inspect = args[0].equals("inspect"), follow = args[0].equals("follow");
        var topics = TABLES.stream().map(t -> PREFIX + t).toList();
        var partitions = topics.stream().map(t -> new TopicPartition(t, 0)).toList();
        try (var consumer = new KafkaConsumer<String, String>(properties());
             var db = inspect ? null : database();
             var es = inspect ? null : EsConfiguration.connect("http://127.0.0.1:20339", "", "")) {
            for (String topic : topics) {
                if (consumer.partitionsFor(topic).size() != 1) throw new IllegalStateException("Require 1 partition per topic");
            }
            if (inspect) {
                consumer.assign(partitions);
                consumer.seekToBeginning(partitions);
            } else {
                consumer.subscribe(topics);
                long joinDeadline = System.nanoTime() + Duration.ofSeconds(30).toNanos();
                while (consumer.assignment().isEmpty()) {
                    consumer.poll(Duration.ofMillis(200));
                    if (System.nanoTime() > joinDeadline) throw new IllegalStateException("Assignment timed out");
                }
                if (!consumer.assignment().equals(Set.copyOf(partitions))) throw new IllegalStateException("Use only one F39 consumer");
                // Joining poll may fetch records; rewind before the processing loop.
                var committed = consumer.committed(Set.copyOf(partitions));
                for (var tp : partitions) {
                    if (committed.get(tp) == null) consumer.seekToBeginning(List.of(tp));
                    else consumer.seek(tp, committed.get(tp).offset());
                }
            }
            var ends = consumer.endOffsets(partitions);
            long processed = 0, deadline = System.nanoTime() + Duration.ofSeconds(60).toNanos();
            while (follow || partitions.stream().anyMatch(tp -> consumer.position(tp) < ends.get(tp))) {
                for (var record : consumer.poll(Duration.ofMillis(500))) {
                    var output = JSON.createObjectNode();
                    output.put("kind", inspect ? "event" : "applied").put("topic", record.topic())
                        .put("partition", record.partition()).put("offset", record.offset());
                    output.set("key", JSON.readTree(record.key()));
                    if (inspect) {
                        output.set("value", record.value() == null ? JSON.nullNode() : JSON.readTree(record.value()));
                    } else {
                        output.set("projection", JSON.valueToTree(apply(db, es, record)));
                        var tp = new TopicPartition(record.topic(), record.partition());
                        consumer.commitSync(Map.of(tp, new OffsetAndMetadata(record.offset() + 1)));
                        output.put("committed_next", record.offset() + 1);
                    }
                    System.out.println(JSON.writeValueAsString(output));
                    processed++;
                }
                if (!follow && System.nanoTime() > deadline) throw new IllegalStateException("Drain timed out");
            }
            var positions = new HashMap<String, Object>();
            var committed = inspect ? null : consumer.committed(Set.copyOf(partitions));
            for (var tp : partitions) positions.put(tp.topic(), Map.of("observed_end", ends.get(tp),
                "committed_next", inspect || committed.get(tp) == null ? -1 : committed.get(tp).offset()));
            System.out.println(JSON.writeValueAsString(Map.of("kind", "summary", "mode", args[0],
                "processed", processed, "positions", positions)));
        }
    }
}
