package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.*;
import co.elastic.clients.elasticsearch._types.query_dsl.*;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

@Service
public class SortSearchService {
    private final ElasticsearchClient client;
    private final String index;
    private final JsonMapper json;

    public SortSearchService(ElasticsearchClient client,
            @Value("${travel.f10-index:tut-f10-attractions}") String index, JsonMapper json) {
        this.client = client; this.index = index; this.json = json;
    }

    public SearchRequest request(SortInput input) {
        var bool = new BoolQuery.Builder()
                .must(m -> m.multiMatch(t -> t.query(input.q()).fields("name^3", "aliases^2", "description")
                        .type(TextQueryType.BestFields).operator(Operator.And).tieBreaker(0.0)))
                .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                        .gte(0.0).lte(input.maxPriceFen().doubleValue()))))
                .filter(f -> f.term(t -> t.field("status").value("open")));
        if (!input.cityCode().equals("ALL")) {
            bool.filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())));
        }
        var search = new SearchRequest.Builder().index(index).size(20)
                .trackTotalHits(t -> t.enabled(true)).trackScores(input.trackScores())
                .source(src -> src.filter(f -> f.includes(List.of("attraction_id", "name", "city_code",
                        "ticket_price_fen", "currency", "status", "location"))))
                .query(q -> q.bool(bool.build()));
        switch (input.sortMode()) {
            case "relevance" -> search.sort(s -> s.score(f -> f.order(SortOrder.Desc)));
            case "price" -> search.sort(s -> s.field(f -> f.field("ticket_price_fen")
                    .order(SortOrder.Asc).missing(FieldValue.of("_last"))));
            case "distance" -> search.sort(s -> s.geoDistance(g -> g.field("location")
                    .location(l -> l.latlon(p -> p.lat(input.latitude()).lon(input.longitude())))
                    .order(SortOrder.Asc).unit(DistanceUnit.Kilometers)
                    .distanceType(GeoDistanceType.Arc).mode(SortMode.Min).ignoreUnmapped(false)));
            default -> throw new IllegalArgumentException("Unsupported sort mode");
        }
        return search.sort(s -> s.field(f -> f.field("attraction_id").order(SortOrder.Asc))).build();
    }

    private Object sortValue(FieldValue value) {
        return switch (value._kind()) {
            case Double -> value.doubleValue();
            case Long -> value.longValue();
            case String -> value.stringValue();
            case Null -> null;
            default -> throw new AttractionSearchService.IncompleteSearchException();
        };
    }

    public SortResult search(SortInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, SortAttraction.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0 || response.hits().total() == null) {
            throw new AttractionSearchService.IncompleteSearchException();
        }
        var items = response.hits().hits().stream().map(hit -> {
            var src = hit.source();
            if (src == null || !hit.id().equals(src.attractionId()) || src.name() == null
                    || src.ticketPriceFen() == null || hit.sort().size() != 2) {
                throw new AttractionSearchService.IncompleteSearchException();
            }
            var values = hit.sort().stream().map(this::sortValue).toList();
            Double distanceKm = null;
            if (input.sortMode().equals("distance") && src.location() != null) {
                if (!(values.getFirst() instanceof Number number) || !Double.isFinite(number.doubleValue())) {
                    throw new AttractionSearchService.IncompleteSearchException();
                }
                distanceKm = number.doubleValue();
            }
            return new SortResult.Card(hit.id(), src.name(), src.cityCode(), src.ticketPriceFen(),
                    src.currency(), src.status(), hit.score(), values, src.location() != null, distanceKm);
        }).toList();
        String dsl = JsonpUtils.toJsonString(request, client._jsonpMapper());
        return new SortResult(response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), input, json.readTree(dsl), items);
    }
}
