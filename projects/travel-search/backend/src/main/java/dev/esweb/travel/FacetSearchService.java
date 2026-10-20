package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.FieldValue;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.aggregations.Aggregate;
import co.elastic.clients.elasticsearch._types.aggregations.Aggregation;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import co.elastic.clients.elasticsearch._types.query_dsl.TextQueryType;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonpUtils;
import co.elastic.clients.util.NamedValue;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

@Service
public class FacetSearchService {
    private final ElasticsearchClient client;
    private final String index;
    private final JsonMapper json;

    public FacetSearchService(ElasticsearchClient client,
            @Value("${travel.f09-index:tut-f09-attractions}") String index, JsonMapper json) {
        this.client = client; this.index = index; this.json = json;
    }

    private Query chosen(String field, List<String> values) {
        if (values.isEmpty()) return Query.of(q -> q.matchAll(m -> m));
        return Query.of(q -> q.terms(t -> t.field(field)
                .terms(v -> v.value(values.stream().map(FieldValue::of).toList()))));
    }

    private Aggregation values(String field) {
        return Aggregation.of(a -> a.terms(t -> t.field(field).size(10).shardSize(10)
                .showTermDocCountError(true)
                .order(List.of(NamedValue.of("_count", SortOrder.Desc), NamedValue.of("_key", SortOrder.Asc)))));
    }

    public SearchRequest request(FacetInput input) {
        Query cities = chosen("city_code", input.cityCodes());
        Query themes = chosen("themes", input.themes());
        Query selection = Query.of(q -> q.bool(b -> b.filter(List.of(cities, themes))));
        return SearchRequest.of(s -> s.index(index).size(20).trackTotalHits(t -> t.enabled(true))
                .source(src -> src.filter(f -> f.includes(List.of("attraction_id", "name", "city_code",
                        "ticket_price_fen", "currency", "status", "themes"))))
                .query(q -> q.bool(b -> b
                        .must(m -> m.multiMatch(t -> t.query(input.q()).fields("name^3", "aliases^2", "description")
                                .type(TextQueryType.BestFields).operator(Operator.And).tieBreaker(0.0)))
                        .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                        .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                                .gte(0.0).lte(input.maxPriceFen().doubleValue()))))
                        .filter(f -> f.term(t -> t.field("status").value("open")))))
                .postFilter(selection)
                .aggregations("cities", a -> a.filter(themes).aggregations("values", values("city_code")))
                .aggregations("themes", a -> a.filter(cities).aggregations("values", values("themes"))
                        .aggregations("missing_theme", x -> x.filter(f -> f.bool(b -> b
                                .mustNot(n -> n.exists(e -> e.field("themes")))))))
                .aggregations("prices", a -> a.filter(selection).aggregations("ranges", x -> x.range(r -> r
                        .field("ticket_price_fen")
                        .ranges(v -> v.key("under-100").from(0.0).to(10000.0))
                        .ranges(v -> v.key("100-to-200").from(10000.0).to(20000.0))
                        .ranges(v -> v.key("200-plus").from(20000.0)))))
                .sort(sort -> sort.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    private FacetResult.TermsFacet termsFacet(Aggregate aggregate, String scope) {
        if (aggregate == null || !aggregate.isFilter()) throw new AttractionSearchService.IncompleteSearchException();
        var group = aggregate.filter();
        var value = group.aggregations().get("values");
        if (value == null || !value.isSterms()) throw new AttractionSearchService.IncompleteSearchException();
        var terms = value.sterms();
        if (terms.docCountErrorUpperBound() == null || terms.sumOtherDocCount() == null
                || !terms.buckets().isArray()) throw new AttractionSearchService.IncompleteSearchException();
        var buckets = terms.buckets().array().stream().map(b -> {
            if (b.docCountErrorUpperBound() == null) throw new AttractionSearchService.IncompleteSearchException();
            return new FacetResult.Bucket(b.key().stringValue(), b.docCount(), b.docCountErrorUpperBound());
        }).toList();
        return new FacetResult.TermsFacet(scope, group.docCount(), terms.docCountErrorUpperBound(),
                terms.sumOtherDocCount(), buckets);
    }

    public FacetResult search(FacetInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, FacetAttraction.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0 || response.hits().total() == null) {
            throw new AttractionSearchService.IncompleteSearchException();
        }
        var items = response.hits().hits().stream().map(hit -> {
            var src = hit.source();
            if (src == null || !hit.id().equals(src.attractionId()) || src.name() == null
                    || src.ticketPriceFen() == null) throw new AttractionSearchService.IncompleteSearchException();
            return new FacetResult.Card(hit.id(), src.name(), src.cityCode(), src.ticketPriceFen(),
                    src.currency(), src.status(), src.themes() == null ? List.of() : src.themes());
        }).toList();
        var cities = termsFacet(response.aggregations().get("cities"), "base AND selected themes; city ignored");
        var themes = termsFacet(response.aggregations().get("themes"), "base AND selected cities; theme ignored");
        var missing = response.aggregations().get("themes").filter().aggregations().get("missing_theme");
        var priceGroup = response.aggregations().get("prices");
        if (missing == null || !missing.isFilter() || priceGroup == null || !priceGroup.isFilter()) {
            throw new AttractionSearchService.IncompleteSearchException();
        }
        var ranges = priceGroup.filter().aggregations().get("ranges");
        if (ranges == null || !ranges.isRange() || !ranges.range().buckets().isArray()) {
            throw new AttractionSearchService.IncompleteSearchException();
        }
        var prices = ranges.range().buckets().array().stream().map(b ->
                new FacetResult.RangeBucket(b.key(), b.from(), b.to(), b.docCount())).toList();
        String dsl = JsonpUtils.toJsonString(request, client._jsonpMapper());
        return new FacetResult(response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), input, json.readTree(dsl), items, cities, themes, missing.filter().docCount(),
                priceGroup.filter().docCount(), prices);
    }
}
