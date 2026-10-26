package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortMode;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.BoolQuery;
import co.elastic.clients.elasticsearch._types.query_dsl.ChildScoreMode;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonData;
import co.elastic.clients.json.JsonpSerializable;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class NestedSearchService {
    private final ElasticsearchClient client;
    private final JsonMapper json;
    public NestedSearchService(ElasticsearchClient client, JsonMapper json) { this.client = client; this.json = json; }
    public record Offer(String offerId, String roomId, String planId, long priceMinor, JsonNode source) {}
    public record Card(String id, String hotelName, Long sortPriceMinor, long matchingOffers, List<Offer> offers, JsonNode source) {}
    public record Result(String model, long total, NestedInput conditions, String boundary, JsonNode esRequest, JsonNode esResponse, List<Card> items) {}

    public Query eligible() {
        var b = new BoolQuery.Builder();
        for (String[] pair : new String[][]{{"bed_type", "twin"}, {"meal", "breakfast"},
                {"cancellation", "flexible"}, {"rate_plan_id", "bf-flex"}, {"currency", "CNY"},
                {"offer_status", "active"}, {"service_date", "2026-11-01"}}) {
            b.filter(q -> q.term(t -> t.field("rooms." + pair[0]).value(pair[1])));
        }
        b.filter(q -> q.range(r -> r.number(n -> n.field("rooms.capacity").gte(2.0))));
        b.filter(q -> q.range(r -> r.number(n -> n.field("rooms.price_minor").gte(0.0).lte(70000.0))));
        return Query.of(q -> q.bool(b.build()));
    }
    public SearchRequest request(NestedInput input) {
        Query eligible = eligible(); // one predicate for matching, inner_hits and sort.filter
        String mode = input.mode();
        var root = new BoolQuery.Builder()
                .filter(q -> q.term(t -> t.field("city_code").value("HZ")))
                .filter(q -> q.term(t -> t.field("hotel_status").value("open")));
        if (mode.equals("object")) root.filter(eligible.bool().filter());
        else if (mode.equals("split")) {
            for (Query atom : eligible.bool().filter())
                root.filter(q -> q.nested(n -> n.path("rooms").scoreMode(ChildScoreMode.None).query(atom)));
        } else {
            root.filter(q -> q.nested(n -> n.path("rooms").scoreMode(ChildScoreMode.None).query(eligible)
                    .innerHits(i -> i.name("eligible").size(1)
                            .sort(s -> s.field(f -> f.field("rooms.price_minor").order(SortOrder.Asc)))
                            .sort(s -> s.field(f -> f.field("rooms.offer_id").order(SortOrder.Asc))))));
        }
        var search = new SearchRequest.Builder().index("tut-f24-" + (mode.equals("object") ? "object" : "nested"))
                .size(20).trackTotalHits(t -> t.enabled(true)).query(q -> q.bool(root.build()));
        if (mode.endsWith("-sort")) search.sort(s -> s.field(f -> f.field("rooms.price_minor")
                .order(SortOrder.Asc).mode(SortMode.Min).missing("_last").nested(n -> {
                    n.path("rooms");
                    if (mode.equals("filtered-sort")) n.filter(eligible);
                    return n;
                })));
        return search.sort(s -> s.field(f -> f.field("hotel_id").order(SortOrder.Asc))).build();
    }
    private JsonNode tree(JsonpSerializable value) { return json.readTree(JsonpUtils.toJsonString(value, client._jsonpMapper())); }
    private void require(boolean condition) { if (!condition) throw new AttractionSearchService.IncompleteSearchException(); }
    private boolean text(JsonNode s, String key) { return s != null && s.hasNonNull(key) && s.get(key).isString() && !s.get(key).asString().isBlank(); }
    private Offer offer(JsonNode s) {
        for (String key : List.of("offer_id", "room_id", "room_name", "bed_type", "meal", "cancellation", "rate_plan_id", "currency", "offer_status", "service_date", "snapshot_at")) require(text(s, key));
        require(s.hasNonNull("capacity") && s.get("capacity").isIntegralNumber() && s.get("capacity").asInt() >= 2);
        require(s.hasNonNull("price_minor") && s.get("price_minor").isIntegralNumber());
        long price = s.get("price_minor").asLong(); require(price >= 0 && price <= 70000);
        require(s.get("bed_type").asString().equals("twin") && s.get("meal").asString().equals("breakfast")
                && s.get("cancellation").asString().equals("flexible") && s.get("rate_plan_id").asString().equals("bf-flex")
                && s.get("currency").asString().equals("CNY") && s.get("offer_status").asString().equals("active")
                && s.get("service_date").asString().equals("2026-11-01") && s.get("snapshot_at").asString().equals("2026-10-26T00:00:00Z"));
        return new Offer(s.get("offer_id").asString(), s.get("room_id").asString(), s.get("rate_plan_id").asString(), price, s);
    }
    public Result inspect(NestedInput input) throws IOException {
        var request = request(input); var response = client.search(request, JsonData.class);
        require(!response.timedOut() && response.shards().failed().longValue() == 0 && response.hits().total() != null && response.hits().total().relation().jsonValue().equals("eq"));
        JsonNode raw = tree(response); List<Card> cards = new ArrayList<>();
        boolean correctSelection = !input.mode().equals("object") && !input.mode().equals("split");
        for (JsonNode hit : raw.get("hits").get("hits")) {
            JsonNode source = hit.get("_source");
            require(text(source, "hotel_id") && text(source, "hotel_name") && text(source, "city_code") && text(source, "hotel_status"));
            String id = hit.get("_id").asString();
            require(id.equals(source.get("hotel_id").asString()) && source.get("city_code").asString().equals("HZ") && source.get("hotel_status").asString().equals("open") && source.hasNonNull("rooms") && source.get("rooms").isArray());
            List<Offer> offers = new ArrayList<>(); long matching = 0;
            if (correctSelection) {
                require(hit.hasNonNull("inner_hits") && hit.get("inner_hits").hasNonNull("eligible"));
                JsonNode inner = hit.get("inner_hits").get("eligible").get("hits");
                require(inner != null && inner.hasNonNull("total") && inner.get("total").get("relation").asString().equals("eq") && inner.get("total").get("value").asLong() > 0 && inner.get("hits").size() == 1);
                matching = inner.get("total").get("value").asLong();
                for (JsonNode nested : inner.get("hits")) {
                    require(nested.hasNonNull("_nested") && nested.get("_nested").get("field").asString().equals("rooms"));
                    int offset = nested.get("_nested").get("offset").asInt();
                    require(offset >= 0 && offset < source.get("rooms").size());
                    require(nested.get("_source").equals(source.get("rooms").get(offset)));
                    Offer selected = offer(nested.get("_source"));
                    require(nested.get("sort").get(0).asLong() == selected.priceMinor() && nested.get("sort").get(1).asString().equals(selected.offerId())); offers.add(selected);
                }
            }
            boolean sorted = input.mode().endsWith("-sort"); require(hit.get("sort").size() == (sorted ? 2 : 1));
            Long sortPrice = sorted ? hit.get("sort").get(0).asLong() : null;
            require(hit.get("sort").get(sorted ? 1 : 0).asString().equals(id));
            if (input.mode().equals("filtered-sort")) require(sortPrice == offers.getFirst().priceMinor());
            cards.add(new Card(id, source.get("hotel_name").asString(), sortPrice, matching, List.copyOf(offers), source));
        }
        return new Result(input.mode().equals("object") ? "object" : "nested", response.hits().total().value(), input,
                "固定单晚报价快照；object/split与unfiltered-sort为故意错误对照；inner_hits每酒店前1条，非完整合格集合；非实时可预订。", tree(request), raw, List.copyOf(cards));
    }
}
