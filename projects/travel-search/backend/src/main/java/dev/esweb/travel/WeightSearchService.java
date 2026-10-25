package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.BoolQuery;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import co.elastic.clients.elasticsearch.core.ExplainRequest;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonpSerializable;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.List;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class WeightSearchService {
    private static final String INDEX = "tut-f19-attractions";
    private final ElasticsearchClient client;
    private final JsonMapper json;

    public WeightSearchService(ElasticsearchClient client, JsonMapper json) {
        this.client = client;
        this.json = json;
    }

    public record Card(String id, String name, String description, String cityCode,
                       int ticketPriceFen, String currency, String status, Double score,
                       List<Object> sortValues, JsonNode explanation) {}
    public record Result(long total, String relation, long tookMs, WeightInput conditions,
                         JsonNode esRequest, JsonNode esResponse, String explainPath,
                         JsonNode explainRequest, JsonNode explainResponse, List<Card> items) {}

    public SearchRequest request(WeightInput input) {
        Query name = Query.of(q -> q.match(m -> m.field("name").query(input.q())
                .operator(Operator.And).boost(input.nameWeight().floatValue())));
        Query description = Query.of(q -> q.match(m -> m.field("description").query(input.q())
                .operator(Operator.And).boost(1.0f)));
        Query combined = input.mode().equals("sum")
                ? Query.of(q -> q.bool(b -> b.should(name, description).minimumShouldMatch("1")))
                : Query.of(q -> q.disMax(d -> d.queries(name, description)
                        .tieBreaker(input.mode().equals("best") ? 0.0 : 0.1)));
        var bool = new BoolQuery.Builder()
                .filter(f -> f.term(t -> t.field("status").value("open")))
                .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                        .gte(0.0).lte(input.maxPriceFen().doubleValue()))))
                .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())));
        if (input.mode().equals("optional") || input.mode().equals("required")) {
            bool.should(combined);
            if (input.mode().equals("required")) bool.minimumShouldMatch("1");
        } else {
            bool.must(combined);
            if (input.mode().equals("tuned")) {
                bool.should(q -> q.matchPhrase(m -> m.field("name").query(input.q()).slop(0).boost(4.0f)));
                bool.should(q -> q.constantScore(c -> c.filter(f -> f.term(t ->
                        t.field("name.exact").value(input.q()))).boost(8.0f)));
                bool.minimumShouldMatch("0");
            }
        }
        return SearchRequest.of(s -> s.index(INDEX).size(20)
                .trackTotalHits(t -> t.enabled(true)).explain(true)
                .query(q -> q.bool(bool.build()))
                .sort(srt -> srt.score(sco -> sco.order(SortOrder.Desc)))
                .sort(srt -> srt.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    private JsonNode tree(JsonpSerializable value) {
        return json.readTree(JsonpUtils.toJsonString(value, client._jsonpMapper()));
    }

    public Result search(WeightInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, WeightAttraction.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0
                || response.hits().total() == null || !response.hits().total().relation().jsonValue().equals("eq"))
            throw new AttractionSearchService.IncompleteSearchException();
        var cards = response.hits().hits().stream().map(hit -> {
            var s = hit.source();
            if (s == null || !hit.id().equals(s.attractionId()) || s.name() == null
                    || s.description() == null || !input.cityCode().equals(s.cityCode())
                    || !"open".equals(s.status()) || !"CNY".equals(s.currency())
                    || s.ticketPriceFen() == null || s.ticketPriceFen() < 0
                    || s.ticketPriceFen() > input.maxPriceFen() || hit.score() == null
                    || hit.explanation() == null || hit.sort().size() != 2)
                throw new AttractionSearchService.IncompleteSearchException();
            return new Card(hit.id(), s.name(), s.description(), s.cityCode(), s.ticketPriceFen(),
                    s.currency(), s.status(), hit.score(), hit.sort().stream().map(v -> (Object) v._get()).toList(),
                    tree(hit.explanation()));
        }).toList();
        // Both calls use the same complete query, including filters. No writes occur in this observer.
        // They are separate requests, not one atomic snapshot under concurrent updates.
        var explainRequest = ExplainRequest.of(e -> e.index(INDEX).id(input.explainId()).query(request.query()));
        var explained = client.explain(explainRequest, WeightAttraction.class);
        if (!INDEX.equals(explained.index()) || !input.explainId().equals(explained.id())
                || explained.explanation() == null)
            throw new AttractionSearchService.IncompleteSearchException();
        return new Result(response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), input, tree(request), tree(response),
                "/" + INDEX + "/_explain/" + input.explainId(), tree(explainRequest), tree(explained), cards);
    }
}
