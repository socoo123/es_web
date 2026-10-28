import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.ElasticsearchException;
import co.elastic.clients.json.JsonData;
import co.elastic.clients.json.JsonpUtils;
import co.elastic.clients.json.jackson.Jackson3JsonpMapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import tools.jackson.databind.json.JsonMapper;

/** One official-client write per invocation. No new application endpoint. */
public class AliasWriter {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) throw new IllegalArgumentException("target id fixture.json");
        String url = System.getenv().getOrDefault("ES_URL", "http://127.0.0.1:19733");
        if (!List.of("http://127.0.0.1:19733", "http://127.0.0.1:19734").contains(url)
                || !List.of("tut-f33-attractions-write", "tut-f33-attractions-read",
                    "tut-f33-missing-write", "tut-f33-attractions-v002").contains(args[0])) {
            throw new IllegalArgumentException("Use the isolated F33 targets");
        }
        JsonMapper json = new JsonMapper();
        JsonData document = JsonData.fromJson(Files.readString(Path.of(args[2])));
        try (var client = ElasticsearchClient.of(b -> b.host(url).jsonMapper(new Jackson3JsonpMapper()))) {
            try {
                var response = client.index(i -> i.index(args[0]).id(args[1])
                        .requireAlias(true).waitForActiveShards(w -> w.count(2)).document(document));
                System.out.println(json.writeValueAsString(Map.of("ok", true, "response",
                        json.readTree(JsonpUtils.toJsonString(response, client._jsonpMapper())))));
            } catch (ElasticsearchException e) {
                System.out.println(json.writeValueAsString(Map.of("ok", false, "status", e.status(),
                        "error", json.readTree(JsonpUtils.toJsonString(e.response(), client._jsonpMapper())))));
            }
        }
    }
}
