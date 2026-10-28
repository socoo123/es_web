import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.ElasticsearchException;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonpSerializable;
import co.elastic.clients.json.JsonpUtils;
import co.elastic.clients.json.jackson.Jackson3JsonpMapper;
import dev.esweb.travel.AttractionSearchService;
import dev.esweb.travel.SearchInput;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import tools.jackson.databind.json.JsonMapper;

/** Standalone official-client lab; reuses F07 query builder, adds no web endpoint. */
public class RoutingLab {
    static final String INDEX = "tut-f29-routed";
    static final String RIGHT = "HZ", WRONG = "SH", COLLISION = "FZ";
    static final JsonMapper JSON = new JsonMapper();
    static final List<Map<String, Object>> EVENTS = new ArrayList<>();

    static void check(boolean ok, String why) {
        if (!ok) throw new IllegalStateException(why);
    }

    static void record(ElasticsearchClient client, String method, String path, Object body,
                       JsonpSerializable response) {
        EVENTS.add(Map.of("method", method, "path", path, "request", body,
                "response", JSON.readTree(JsonpUtils.toJsonString(response, client._jsonpMapper()))));
    }

    static List<String> ids(co.elastic.clients.elasticsearch.core.SearchResponse<Map> response) {
        check(!response.timedOut() && response.shards().failed().longValue() == 0
                && response.hits().total() != null && response.hits().total().relation().jsonValue().equals("eq"),
                "Incomplete search must not become an empty success");
        return response.hits().hits().stream().map(h -> h.id()).toList();
    }

    public static void main(String[] args) throws Exception {
        String url = System.getenv().getOrDefault("ES_URL", "http://127.0.0.1:19330");
        check(List.of("http://127.0.0.1:19329", "http://127.0.0.1:19330", "http://127.0.0.1:19331")
                .contains(url), "Use an isolated F29 endpoint");
        try (var client = ElasticsearchClient.of(b -> b.host(url).jsonMapper(new Jackson3JsonpMapper()))) {
            var fixture = JSON.readTree(Files.readString(Path.of("data/f29/routed.json")));
            Map<String, Object> source = JSON.convertValue(fixture.get(0).get("source"), Map.class);
            source.put("attraction_id", "java-probe");
            String path = "/" + INDEX + "/_doc/java-probe?routing=" + RIGHT;
            var absent = client.get(g -> g.index(INDEX).id("java-probe").routing(RIGHT), Map.class);
            record(client, "GET", path, Map.of(), absent);
            check(!absent.found(), "Probe exists: inspect and clean explicitly before repeating");
            var written = client.index(i -> i.index(INDEX).id("java-probe").routing(RIGHT)
                    .waitForActiveShards(w -> w.count(2)).document(source));
            record(client, "PUT", path + "&wait_for_active_shards=2", source, written);
            check(written.result().jsonValue().equals("created") && written.shards().successful().intValue() == 2,
                    "Expected primary plus replica write");
            var got = client.get(g -> g.index(INDEX).id("java-probe").routing(RIGHT), Map.class);
            record(client, "GET", path, Map.of(), got);
            check(got.found() && got.source().equals(source), "GET must use the write routing");
            var updated = client.update(u -> u.index(INDEX).id("java-probe").routing(RIGHT)
                    .doc(Map.of("ticket_price_fen", 7100)), Map.class);
            record(client, "POST", "/" + INDEX + "/_update/java-probe?routing=" + RIGHT,
                    Map.of("doc", Map.of("ticket_price_fen", 7100)), updated);
            check(updated.result().jsonValue().equals("updated"), "Update failed");
            var changed = client.get(g -> g.index(INDEX).id("java-probe").routing(RIGHT), Map.class);
            record(client, "GET", path, Map.of(), changed);
            check(((Number) changed.source().get("ticket_price_fen")).intValue() == 7100, "Wrong updated price");
            var deleted = client.delete(d -> d.index(INDEX).id("java-probe").routing(RIGHT));
            record(client, "DELETE", path, Map.of(), deleted);
            check(deleted.result().jsonValue().equals("deleted"), "Delete failed");
            var gone = client.get(g -> g.index(INDEX).id("java-probe").routing(RIGHT), Map.class);
            record(client, "GET", path, Map.of(), gone);
            check(!gone.found(), "Delete did not remove probe");
            var service = new AttractionSearchService(client, INDEX, JSON);
            var input = new SearchInput("西湖", "HZ", 20000, 30.25, 120.15, 3.0);
            String dsl = JsonpUtils.toJsonString(service.request(input), client._jsonpMapper());
            for (String route : List.of("", RIGHT, WRONG)) {
                SearchRequest request = SearchRequest.of(s -> {
                    s.withJson(new StringReader(dsl)).index(INDEX).allowPartialSearchResults(false);
                    if (!route.isEmpty()) s.routing(route);
                    return s;
                });
                var result = client.search(request, Map.class);
                record(client, "POST", "/" + INDEX + "/_search?allow_partial_search_results=false"
                        + (route.isEmpty() ? "" : "&routing=" + route), JSON.readTree(dsl), result);
                check(ids(result).equals(route.equals(WRONG) ? List.of() : List.of("r01", "r02")), "Search IDs differ");
                check(result.shards().total().intValue() == (route.isEmpty() ? 2 : 1), "Wrong target shard count");
            }
            var wrong = client.get(g -> g.index(INDEX).id("r01").routing(WRONG), Map.class);
            record(client, "GET", "/" + INDEX + "/_doc/r01?routing=" + WRONG, Map.of(), wrong);
            check(!wrong.found(), "Cross-shard routing premise failed");
            var collision = client.get(g -> g.index(INDEX).id("r01").routing(COLLISION), Map.class);
            record(client, "GET", "/" + INDEX + "/_doc/r01?routing=" + COLLISION, Map.of(), collision);
            check(collision.found() && collision.routing().equals(RIGHT), "Same-shard wrong routing must demonstrate the caveat");
            try {
                client.get(g -> g.index(INDEX).id("r01"), Map.class);
                throw new IllegalStateException("Missing routing was accepted");
            } catch (ElasticsearchException e) {
                check(e.status() == 400 && e.error().type().equals("routing_missing_exception"), "Unexpected rejection");
                EVENTS.add(Map.of("method", "GET", "path", "/" + INDEX + "/_doc/r01",
                        "status", e.status(), "error_type", e.error().type()));
            }
            System.out.println(JSON.writeValueAsString(Map.of("passed", true, "sdk_calls", EVENTS.size(),
                    "index", INDEX, "events", EVENTS, "dsl", JSON.readTree(dsl))));
        }
    }
}
