import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonData;
import java.nio.file.Files;
import java.nio.file.Path;

/** Run only while m1 is alive and both F30 data nodes are stopped. */
public class FailureProbe {
    public static void main(String[] args) throws Exception {
        try (var client = ElasticsearchClient.of(b -> b.host("http://127.0.0.1:19430"));
             var input = Files.newInputStream(Path.of("search/f30/search.json"))) {
            var request = SearchRequest.of(b -> b.index("tut-f30-attractions").withJson(input));
            try {
                client.search(request, JsonData.class);
                throw new AssertionError("Expected a search failure with both data nodes down");
            } catch (java.io.IOException error) {
                // Same superclass handled by the existing ApiErrors.unavailable branch.
                System.out.println("top=" + error.getClass().getName());
                System.out.println("message=" + error.getMessage());
                for (Throwable cause = error.getCause(); cause != null; cause = cause.getCause()) {
                    System.out.println("cause=" + cause.getClass().getName() + ": " + cause.getMessage());
                }
                if (!error.getClass().getName().equals("co.elastic.clients.transport.rest5_client.low_level.ResponseException")
                        || !error.getMessage().contains("503")) {
                    throw new AssertionError("Different failure from this lesson's observation", error);
                }
            }
        }
    }
}
