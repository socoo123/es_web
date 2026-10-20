package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.GeoDistanceType;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

@Service
public class AttractionSearchService {
    private final ElasticsearchClient client;
    private final String index;
    private final JsonMapper json;

    public AttractionSearchService(ElasticsearchClient client,
            @Value("${travel.index}") String index, JsonMapper json) {
        this.client = client;
        this.index = index;
        this.json = json;
    }

    public SearchRequest request(SearchInput input) {
        return SearchRequest.of(search -> search.index(index)
                .size(20).trackTotalHits(t -> t.enabled(true)).trackScores(true)
                .source(s -> s.filter(f -> f.includes(List.of("attraction_id", "name", "city_code",
                        "ticket_price_fen", "currency", "status", "location"))))
                .query(q -> q.bool(b -> b
                        .must(m -> m.match(t -> t.field("name").query(input.q()).operator(Operator.Or)))
                        .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())))
                        .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                        .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                                .gte(0.0).lte(input.maxPriceFen().doubleValue()))))
                        .filter(f -> f.term(t -> t.field("status").value("open")))
                        .filter(f -> f.geoDistance(g -> g.field("location")
                                .distance(input.radiusKm() + "km").distanceType(GeoDistanceType.Arc)
                                .location(l -> l.latlon(p -> p.lat(input.latitude()).lon(input.longitude())))))))
                .sort(s -> s.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    public SearchResult search(SearchInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, Attraction.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0
                || response.hits().total() == null) {
            throw new IncompleteSearchException();
        }
        var items = response.hits().hits().stream().map(hit -> {
            var source = hit.source();
            if (source == null || !hit.id().equals(source.attractionId())
                    || source.name() == null || source.ticketPriceFen() == null) {
                throw new IncompleteSearchException();
            }
            return new SearchResult.Card(hit.id(), source.name(), source.cityCode(),
                    source.ticketPriceFen(), source.currency(), source.status(), hit.score());
        }).toList();
        String dsl = JsonpUtils.toJsonString(request, client._jsonpMapper());
        return new SearchResult(response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), input, json.readTree(dsl), items);
    }

    public static class IncompleteSearchException extends RuntimeException {
    }
}
