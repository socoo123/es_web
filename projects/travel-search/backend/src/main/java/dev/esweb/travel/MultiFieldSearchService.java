package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.GeoDistanceType;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.TextQueryType;
import co.elastic.clients.elasticsearch.core.search.HighlighterEncoder;
import co.elastic.clients.elasticsearch.core.search.HighlighterType;
import co.elastic.clients.elasticsearch.core.search.HighlightField;
import co.elastic.clients.util.NamedValue;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

@Service
public class MultiFieldSearchService {
    private final ElasticsearchClient client;
    private final String index;
    private final JsonMapper json;

    public MultiFieldSearchService(ElasticsearchClient client,
            @Value("${travel.f08-index:tut-f08-attractions}") String index, JsonMapper json) {
        this.client = client;
        this.index = index;
        this.json = json;
    }

    public SearchRequest request(SearchInput input) {
        return SearchRequest.of(search -> search.index(index)
                .size(20).trackTotalHits(t -> t.enabled(true)).trackScores(true)
                .source(s -> s.filter(f -> f.includes(List.of("attraction_id", "name", "city_code",
                        "ticket_price_fen", "currency", "status", "location", "aliases", "description"))))
                .query(q -> q.bool(b -> b
                        .must(m -> m.multiMatch(t -> t.query(input.q())
                                .fields("name^3", "aliases^2", "description")
                                .type(TextQueryType.BestFields).operator(Operator.And).tieBreaker(0.0)))
                        .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())))
                        .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                        .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                                .gte(0.0).lte(input.maxPriceFen().doubleValue()))))
                        .filter(f -> f.term(t -> t.field("status").value("open")))
                        .filter(f -> f.geoDistance(g -> g.field("location")
                                .distance(input.radiusKm() + "km").distanceType(GeoDistanceType.Arc)
                                .location(l -> l.latlon(p -> p.lat(input.latitude()).lon(input.longitude())))))))
                .highlight(h -> h.type(HighlighterType.Unified).encoder(HighlighterEncoder.Html)
                        .preTags("<mark>").postTags("</mark>").requireFieldMatch(true)
                        .fields(NamedValue.of("name", HighlightField.of(f -> f.numberOfFragments(0))))
                        .fields(NamedValue.of("aliases", HighlightField.of(f -> f.numberOfFragments(0))))
                        .fields(NamedValue.of("description", HighlightField.of(f -> f.fragmentSize(120).numberOfFragments(1)))))
                .sort(s -> s.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    public MultiFieldResult search(SearchInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, MultiFieldAttraction.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0
                || response.hits().total() == null) {
            throw new AttractionSearchService.IncompleteSearchException();
        }
        var items = response.hits().hits().stream().map(hit -> {
            var source = hit.source();
            if (source == null || !hit.id().equals(source.attractionId())
                    || source.name() == null || source.ticketPriceFen() == null) {
                throw new AttractionSearchService.IncompleteSearchException();
            }
            var highlights = hit.highlight();
            var snippets = List.of(
                    HighlightSegments.snippet("name", highlights.get("name"), source.name()),
                    HighlightSegments.snippet("aliases", highlights.get("aliases"),
                            source.aliases() == null || source.aliases().isEmpty() ? "未提供别名" : String.join("、", source.aliases())),
                    HighlightSegments.snippet("description", highlights.get("description"),
                            source.description() == null || source.description().isBlank() ? "暂无描述" : source.description()));
            return new MultiFieldResult.Card(hit.id(), source.name(), source.cityCode(),
                    source.ticketPriceFen(), source.currency(), source.status(), hit.score(), snippets);
        }).toList();
        String dsl = JsonpUtils.toJsonString(request, client._jsonpMapper());
        return new MultiFieldResult(response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), input, json.readTree(dsl), items);
    }

}
