package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.*;
import co.elastic.clients.elasticsearch._types.query_dsl.*;
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
public class DecaySearchService {
    private static final String INDEX = "tut-f21-attractions";
    public static final String AS_OF = "2026-10-01T00:00:00.000Z";
    private final ElasticsearchClient client;
    private final JsonMapper json;

    public DecaySearchService(ElasticsearchClient client, JsonMapper json) {
        this.client = client;
        this.json = json;
    }

    public record Card(String id, String name, String description, String cityCode,
                       int ticketPriceFen, String currency, String status,
                       SortAttraction.Location location, String verifiedAt, Double distanceKm,
                       Double score, List<Object> sortValues, JsonNode explanation) {}
    public record Result(long total, String relation, long tookMs, String asOf, DecayInput conditions,
                         JsonNode esRequest, JsonNode esResponse, String explainPath,
                         JsonNode explainRequest, JsonNode explainResponse, List<Card> items) {}

    private FunctionScore missingZero(String field) {
        // SUM with only zero weights falls back to 1 in ES9.4.0. A real zero function with weight 1 avoids it.
        return FunctionScore.of(f -> f.weight(1.0)
                .filter(q -> q.bool(b -> b.mustNot(n -> n.exists(e -> e.field(field)))))
                .scriptScore(s -> s.script(v -> v.source(x -> x.scriptString("0.0")).lang("painless"))));
    }

    public SearchRequest request(DecayInput input) {
        GeoLocation origin = GeoLocation.of(g -> g.latlon(p -> p.lat(input.latitude()).lon(input.longitude())));
        Query text = Query.of(q -> q.match(m -> m.field("description").query(input.q()).operator(Operator.Or)));
        var bool = new BoolQuery.Builder().must(text)
                .filter(f -> f.term(t -> t.field("status").value("open")))
                .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                        .gte(0.0).lte(input.maxPriceFen().doubleValue()))))
                .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())))
                .filter(f -> f.bool(b -> b
                        .should(q -> q.range(r -> r.date(d -> d.field("verified_at").lte(AS_OF))))
                        .should(q -> q.bool(n -> n.mustNot(m -> m.exists(e -> e.field("verified_at")))))
                        .minimumShouldMatch("1")));
        if (input.radiusKm() != null) bool.filter(f -> f.geoDistance(g -> g.field("location")
                .location(origin).distance(input.radiusKm() + "km").distanceType(GeoDistanceType.Arc)));
        Query base = Query.of(q -> q.bool(bool.build()));
        Query scored = base;
        if (!input.mode().equals("text")) {
            boolean guarded = !input.mode().equals("bare");
            var geo = new FunctionScore.Builder().weight(0.5);
            var time = new FunctionScore.Builder().weight(0.3);
            if (guarded) {
                geo.filter(q -> q.exists(e -> e.field("location")));
                time.filter(q -> q.exists(e -> e.field("verified_at")));
            }
            FunctionScore distance = geo.gauss(d -> d.geo(g -> g.field("location")
                    .placement(p -> p.origin(origin).scale("5km").offset("1km").decay(0.5)))).build();
            FunctionScore freshness = time.exp(d -> d.date(t -> t.field("verified_at")
                    .placement(p -> p.origin(AS_OF).scale(Time.of(v -> v.time("30d")))
                            .offset(Time.of(v -> v.time("1d"))).decay(0.5)))).build();
            // Exactly one branch per logical signal matches: real decay, or constant zero for absence.
            List<FunctionScore> functions = guarded
                    ? List.of(distance, missingZero("location"), freshness, missingZero("verified_at"))
                    : List.of(distance, freshness);
            FunctionBoostMode boost = switch (input.mode()) {
                case "multiply" -> FunctionBoostMode.Multiply;
                case "replace" -> FunctionBoostMode.Replace;
                default -> FunctionBoostMode.Sum;
            };
            scored = Query.of(q -> q.functionScore(f -> f.query(base).functions(functions)
                    .scoreMode(input.mode().equals("product") ? FunctionScoreMode.Multiply : FunctionScoreMode.Sum)
                    .boostMode(boost).maxBoost(0.8)));
        }
        var search = new SearchRequest.Builder().index(INDEX).size(20)
                .trackTotalHits(t -> t.enabled(true)).trackScores(true).explain(true).query(scored);
        switch (input.sortMode()) {
            case "relevance" -> search.sort(s -> s.score(v -> v.order(SortOrder.Desc)));
            case "price" -> search.sort(s -> s.field(v -> v.field("ticket_price_fen")
                    .order(SortOrder.Asc).missing(FieldValue.of("_last"))));
            case "distance" -> search.sort(s -> s.geoDistance(g -> g.field("location").location(origin)
                    .order(SortOrder.Asc).unit(DistanceUnit.Kilometers).distanceType(GeoDistanceType.Arc)
                    .mode(SortMode.Min).ignoreUnmapped(false)));
            default -> throw new IllegalArgumentException("Unsupported sort mode");
        }
        return search.sort(s -> s.field(f -> f.field("attraction_id").order(SortOrder.Asc))).build();
    }

    private JsonNode tree(JsonpSerializable value) {
        return json.readTree(JsonpUtils.toJsonString(value, client._jsonpMapper()));
    }

    public Result search(DecayInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, DecayAttraction.class);
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
                    || hit.explanation() == null || hit.sort().size() != 2
                    || (s.location() != null && (s.location().lat() == null || s.location().lon() == null)))
                throw new AttractionSearchService.IncompleteSearchException();
            var values = hit.sort().stream().map(v -> (Object) v._get()).toList();
            Double distance = null;
            if (input.sortMode().equals("distance") && s.location() != null) {
                if (!(values.getFirst() instanceof Number n) || !Double.isFinite(n.doubleValue()))
                    throw new AttractionSearchService.IncompleteSearchException();
                distance = ((Number) values.getFirst()).doubleValue();
            }
            return new Card(hit.id(), s.name(), s.description(), s.cityCode(), s.ticketPriceFen(),
                    s.currency(), s.status(), s.location(), s.verifiedAt(), distance,
                    hit.score(), values, tree(hit.explanation()));
        }).toList();
        // Complete query reused, including hard eligibility; separate requests are not an atomic snapshot.
        var explainRequest = ExplainRequest.of(e -> e.index(INDEX).id(input.explainId()).query(request.query()));
        var explained = client.explain(explainRequest, DecayAttraction.class);
        if (!INDEX.equals(explained.index()) || !input.explainId().equals(explained.id())
                || explained.explanation() == null)
            throw new AttractionSearchService.IncompleteSearchException();
        return new Result(response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), AS_OF, input, tree(request), tree(response),
                "/" + INDEX + "/_explain/" + input.explainId(), tree(explainRequest), tree(explained), cards);
    }
}
