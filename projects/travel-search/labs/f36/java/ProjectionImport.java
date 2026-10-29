import co.elastic.clients.elasticsearch.core.BulkRequest;
import co.elastic.clients.json.JsonData;
import dev.esweb.travel.EsConfiguration;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;
import tools.jackson.databind.json.JsonMapper;

/** F36 bounded, sequential file import. No event consumer or offset is implemented. */
public class ProjectionImport {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("One projection NDJSON file is required");
        String url = System.getenv().getOrDefault("ES_URL", "http://127.0.0.1:20036");
        String ca = System.getenv().getOrDefault("ES_CA_FILE", "");
        String key = System.getenv().getOrDefault("ES_API_KEY_FILE", "");
        var json = JsonMapper.builder().build();
        var bulk = new BulkRequest.Builder().index("tut-f36-attractions-write").requireAlias(true);
        Set<String> ids = new HashSet<>();
        for (String line : Files.readAllLines(Path.of(args[0]))) {
            if (line.isBlank()) continue;
            var row = json.readTree(line);
            String id = row.path("id").asString();
            String op = row.path("op").asString();
            if (!id.matches("p[0-9]{2}") || !ids.add(id)) {
                throw new IllegalArgumentException("Invalid or duplicate business ID");
            }
            if ("index".equals(op)) {
                var document = row.path("document");
                if (!id.equals(document.path("attraction_id").asString())
                        || !"open".equals(document.path("status").asString())) {
                    throw new IllegalArgumentException("Projection ID/status mismatch");
                }
                var body = JsonData.fromJson(json.writeValueAsString(document));
                bulk.operations(o -> o.index(i -> i.id(id).document(body)));
            } else if ("delete".equals(op) && row.path("document").isNull()) {
                bulk.operations(o -> o.delete(d -> d.id(id)));
            } else {
                throw new IllegalArgumentException("Unsupported projection operation");
            }
        }
        if (ids.isEmpty() || ids.size() > 100) {
            throw new IllegalArgumentException("This teaching importer accepts 1..100 records");
        }
        try (var client = EsConfiguration.connect(url, ca, key)) {
            var response = client.bulk(bulk.build());
            boolean failed = false;
            for (var item : response.items()) {
                boolean absentDelete = item.operationType().jsonValue().equals("delete")
                        && item.status() == 404 && item.error() == null;
                boolean ok = item.error() == null && (item.status() < 300 || absentDelete);
                System.out.printf("%s %s %d %s%n", item.operationType().jsonValue(),
                        item.id(), item.status(), item.result());
                failed |= !ok;
            }
            if (failed || response.items().size() != ids.size()) {
                throw new IllegalStateException("Bulk item failed; stop and inspect; no checkpoint advanced");
            }
        }
    }
}
