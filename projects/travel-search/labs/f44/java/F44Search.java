import co.elastic.clients.elasticsearch._types.ElasticsearchException;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonData;
import co.elastic.clients.json.JsonpUtils;
import dev.esweb.travel.EsConfiguration;
import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import tools.jackson.databind.json.JsonMapper;

/** One bounded diagnostic request; the lesson owns this local endpoint/index. */
public class F44Search {
    public static void main(String[] args) throws Exception {
        var json = JsonMapper.builder().build();
        var result = new LinkedHashMap<String,Object>();
        var body = Files.readString(Path.of(args[0]));
        boolean profile = args.length > 1 && args[1].equals("profile");
        try (var connection = EsConfiguration.connect("http://127.0.0.1:20844", "", "")) {
            var es = connection.withTransportOptions(o -> o.addHeader("X-Opaque-Id", "f44-java"));
            var request = new SearchRequest.Builder().index("tut-f44-attractions")
                .allowPartialSearchResults(false).requestCache(false)
                .withJson(new StringReader(body)).profile(profile).build();
            result.put("request", json.readTree(JsonpUtils.toJsonString(request, es._jsonpMapper())));
            long start = System.nanoTime();
            try {
                var reply = es.search(request, JsonData.class);
                if (reply.timedOut() || reply.shards().failed().intValue() != 0) {
                    throw new IllegalStateException("Incomplete search response");
                }
                result.put("status", 200);
                result.put("reply", json.readTree(JsonpUtils.toJsonString(reply, es._jsonpMapper())));
            } catch (ElasticsearchException e) {
                result.put("status", e.status());
                result.put("type", e.error().type());
                result.put("reason", e.error().reason());
                result.put("error", json.readTree(JsonpUtils.toJsonString(e.error(), es._jsonpMapper())));
                // Preserve the cause. A 429 alone does not identify its mechanism.
            } catch (IOException e) {
                result.put("status", "transport_error");
                result.put("reason", e.getMessage());
                // No blind retry: the caller must first identify the failure.
            }
            result.put("client_ms", (System.nanoTime() - start) / 1e6);
        }
        System.out.println(json.writeValueAsString(result));
    }
}
