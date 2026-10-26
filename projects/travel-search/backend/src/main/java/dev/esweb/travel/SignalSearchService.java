package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.BoolQuery;
import co.elastic.clients.elasticsearch._types.query_dsl.FunctionScoreMode;
import co.elastic.clients.elasticsearch._types.query_dsl.FunctionBoostMode;
import co.elastic.clients.elasticsearch._types.query_dsl.FieldValueFactorModifier;
import co.elastic.clients.elasticsearch._types.query_dsl.FunctionScore;
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
public class SignalSearchService {
    private static final String INDEX = "tut-f20-attractions";
    private final ElasticsearchClient client;
    private final JsonMapper json;

    public SignalSearchService(ElasticsearchClient client, JsonMapper json) {
        this.client = client;
        this.json = json;
    }

    public record Card(String id, String name, String description, String cityCode,
                       int ticketPriceFen, String currency, String status, Double reviewAvg, Long reviewCount, Double qualityScore,
                       Double hot30d, Double score,
                       List<Object> sortValues, JsonNode explanation) {}
    public record Result(long total, String relation, long tookMs, SignalInput conditions,
                         JsonNode esRequest, JsonNode esResponse, String explainPath,
                         JsonNode explainRequest, JsonNode explainResponse, List<Card> items) {}

    public SearchRequest request(SignalInput input) {
        Query text = Query.of(q -> q.match(m -> m.field("description").query(input.q()).operator(Operator.Or)));
        Query feature = Query.of(q -> q.rankFeature(r -> r.field("quality_rank")
                .saturation(v -> v.pivot(4.0f)).boost(1.0f)));
        var bool = new BoolQuery.Builder()
                .filter(f -> f.term(t -> t.field("status").value("open")))
                .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                        .gte(0.0).lte(input.maxPriceFen().doubleValue()))))
                .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())));
        bool.must(input.mode().equals("rank-only") ? feature : text);
        if (input.mode().equals("rank")) bool.should(feature).minimumShouldMatch("0");
        Query base = Query.of(q -> q.bool(bool.build()));
        Query scored = base;
        if (!List.of("text", "rank", "rank-only").contains(input.mode())) {
            FunctionScore quality = FunctionScore.of(f -> f.weight(1.0)
                    .fieldValueFactor(v -> v.field("quality_score").factor(0.2)
                            .modifier(FieldValueFactorModifier.None).missing(4.0)));
            FunctionScore heat = FunctionScore.of(f -> f.weight(0.15)
                    .fieldValueFactor(v -> v.field("hot_30d").factor(1.0)
                            .modifier(FieldValueFactorModifier.Ln1p).missing(0.0)));
            List<FunctionScore> functions = switch (input.mode()) {
                case "raw" -> List.of(FunctionScore.of(f -> f.weight(1.0).fieldValueFactor(v ->
                        v.field("hot_30d").factor(1.0).modifier(FieldValueFactorModifier.None).missing(0.0))));
                case "average" -> List.of(FunctionScore.of(f -> f.weight(1.0).fieldValueFactor(v ->
                        v.field("review_avg").factor(0.2).modifier(FieldValueFactorModifier.None).missing(4.0))));
                case "quality" -> List.of(quality);
                default -> List.of(quality, heat);
            };
            double cap = input.mode().equals("bounded") ? 1.5 : 3.4028235e38;
            scored = Query.of(q -> q.functionScore(f -> f.query(base).functions(functions)
                    .scoreMode(FunctionScoreMode.Sum).boostMode(FunctionBoostMode.Sum).maxBoost(cap)));
        }
        Query finalQuery = scored;
        return SearchRequest.of(s -> s.index(INDEX).size(20)
                .trackTotalHits(t -> t.enabled(true)).explain(true)
                .query(finalQuery)
                .sort(srt -> srt.score(sco -> sco.order(SortOrder.Desc)))
                .sort(srt -> srt.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    private JsonNode tree(JsonpSerializable value) {
        return json.readTree(JsonpUtils.toJsonString(value, client._jsonpMapper()));
    }

    public Result search(SignalInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, SignalAttraction.class);
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
                    s.currency(), s.status(), s.reviewAvg(), s.reviewCount(), s.qualityScore(), s.hot30d(), hit.score(), hit.sort().stream().map(v -> (Object) v._get()).toList(),
                    tree(hit.explanation()));
        }).toList();
        // Both calls use the same complete query, including filters. No writes occur in this observer.
        // They are separate requests, not one atomic snapshot under concurrent updates.
        var explainRequest = ExplainRequest.of(e -> e.index(INDEX).id(input.explainId()).query(request.query()));
        var explained = client.explain(explainRequest, SignalAttraction.class);
        if (!INDEX.equals(explained.index()) || !input.explainId().equals(explained.id())
                || explained.explanation() == null)
            throw new AttractionSearchService.IncompleteSearchException();
        return new Result(response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), input, tree(request), tree(response),
                "/" + INDEX + "/_explain/" + input.explainId(), tree(explainRequest), tree(explained), cards);
    }
}
