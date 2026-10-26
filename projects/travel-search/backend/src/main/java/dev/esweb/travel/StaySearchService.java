package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.BoolQuery;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonData;
import co.elastic.clients.json.JsonpSerializable;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class StaySearchService {
    private final ElasticsearchClient client;
    private final JsonMapper json;
    private final Map<String, JsonNode> table = new LinkedHashMap<>();
    private static final String SNAPSHOT = "f25-20261026-v1";
    public StaySearchService(ElasticsearchClient client, JsonMapper json) throws IOException {
        this.client = client; this.json = json;
        try (var stream = new ClassPathResource("f25/stay-table.json").getInputStream()) {
            JsonNode root = json.readTree(stream);
            require(root.get("snapshot_id").asString().equals(SNAPSHOT));
            for (JsonNode offer : root.get("offers")) {
                JsonNode summary = offer.get("summary"); String id = summary.get("offer_id").asString();
                require(summary.get("snapshot_id").asString().equals(SNAPSHOT) && table.putIfAbsent(id, offer) == null);
                Set<String> dates = new HashSet<>();
                for (JsonNode row : offer.get("nights")) {
                    require(dates.add(LocalDate.parse(row.get("date").asString()).toString()));
                    require(row.get("available_rooms").isIntegralNumber() && row.get("available_rooms").asInt() >= 0);
                    require(row.get("min_stay_arrival").isIntegralNumber() && row.get("min_stay_arrival").asInt() >= 1);
                    require(!row.hasNonNull("price_minor") || (row.get("price_minor").isIntegralNumber() && row.get("price_minor").asLong() >= 0));
                }
            }
        }
    }
    public record Night(String date, Integer availableRooms, Long priceMinor, Integer minStayArrival) {}
    public record Decision(String offerId, String hotelId, String hotelName, String roomId, String planId,
            String currency, String reason, String failedDate, Long totalMinor, List<Night> nights) {}
    public record Result(StayInput conditions, String snapshotId, String boundary, long candidateTotal,
            long acceptedTotal, List<Decision> decisions, JsonNode esRequest, JsonNode esResponse) {}
    private static void require(boolean ok) { if (!ok) throw new AttractionSearchService.IncompleteSearchException(); }
    private JsonNode tree(JsonpSerializable value) { return json.readTree(JsonpUtils.toJsonString(value, client._jsonpMapper())); }
    public SearchRequest request(StayInput input) {
        var b = new BoolQuery.Builder();
        for (String[] pair : new String[][]{{"city_code","HZ"},{"hotel_status","open"},{"offer_status","active"},
                {"bed_type","twin"},{"meal","breakfast"},{"cancellation","flexible"},{"rate_plan_id","bf-flex"},{"currency","CNY"}})
            b.filter(q -> q.term(t -> t.field(pair[0]).value(pair[1])));
        b.filter(q -> q.range(r -> r.number(n -> n.field("capacity").gte(input.adultsPerRoom().doubleValue()))));
        b.filter(q -> q.range(r -> r.date(d -> d.field("window_start").lte(input.checkIn().toString()))));
        b.filter(q -> q.range(r -> r.date(d -> d.field("window_end_exclusive").gte(input.checkOut().toString()))));
        b.filter(q -> q.range(r -> r.number(n -> n.field("max_available_rooms").gte(input.rooms().doubleValue()))));
        return new SearchRequest.Builder().index("tut-f25-offers").size(100).trackTotalHits(t -> t.enabled(true))
                .query(q -> q.bool(b.build())).sort(s -> s.field(f -> f.field("offer_id").order(SortOrder.Asc))).build();
    }
    private Decision decision(JsonNode s, StayInput input) {
        JsonNode offer = table.get(s.get("offer_id").asString());
        require(offer != null && offer.get("summary").equals(s)); // stale or altered ES source is an integrity failure
        Map<String, JsonNode> byDate = new HashMap<>();
        for (JsonNode row : offer.get("nights")) byDate.put(row.get("date").asString(), row);
        List<Night> nights = new ArrayList<>();
        for (LocalDate d = input.checkIn(); d.isBefore(input.checkOut()); d = d.plusDays(1)) {
            JsonNode row = byDate.get(d.toString());
            nights.add(row == null ? new Night(d.toString(), null, null, null) :
                    new Night(d.toString(), row.get("available_rooms").asInt(),
                            row.hasNonNull("price_minor") ? row.get("price_minor").asLong() : null,
                            row.get("min_stay_arrival").asInt()));
        }
        String reason = "ACCEPTED", failed = null; Long total = null;
        long length = ChronoUnit.DAYS.between(input.checkIn(), input.checkOut()), sum = 0;
        Night arrival = nights.getFirst();
        if (arrival.minStayArrival() != null && length < arrival.minStayArrival()) {
            reason = "MIN_STAY"; failed = arrival.date();
        } else for (Night n : nights) {
            if (n.availableRooms() == null) reason = "MISSING_NIGHT";
            else if (n.availableRooms() == 0) reason = "SOLD_OUT";
            else if (n.availableRooms() < input.rooms()) reason = "STOCK_SHORTAGE";
            else if (n.priceMinor() == null) reason = "MISSING_PRICE";
            if (!reason.equals("ACCEPTED")) { failed = n.date(); break; }
            sum = Math.addExact(sum, Math.multiplyExact(n.priceMinor(), input.rooms().longValue()));
        }
        if (reason.equals("ACCEPTED")) {
            total = sum;
            if (sum > input.budgetMinor()) reason = "BUDGET_EXCEEDED";
        }
        return new Decision(s.get("offer_id").asString(), s.get("hotel_id").asString(), s.get("hotel_name").asString(),
                s.get("room_id").asString(), s.get("rate_plan_id").asString(), s.get("currency").asString(),
                reason, failed, total, List.copyOf(nights));
    }
    public Result inspect(StayInput input) throws IOException {
        var request = request(input); var response = client.search(request, JsonData.class);
        require(!response.timedOut() && response.shards().failed().longValue() == 0 && response.hits().total() != null
                && response.hits().total().relation().jsonValue().equals("eq")
                && response.hits().total().value() == response.hits().hits().size()); // never silently accept a truncated candidate set
        List<Decision> decisions = new ArrayList<>(); Set<String> seen = new HashSet<>();
        for (var hit : response.hits().hits()) {
            require(hit.source() != null); JsonNode source = json.readTree(hit.source().toJson().toString());
            require(source.hasNonNull("offer_id") && hit.id().equals(source.get("offer_id").asString()) && seen.add(hit.id()));
            decisions.add(decision(source, input));
        }
        return new Result(input, SNAPSHOT,
                "只核对固定快照的全部ES候选；按offer_id显示，未酒店去重或按总价排序；不含税费，不锁库存，不证明实时可下单。",
                response.hits().total().value(), decisions.stream().filter(d -> d.reason().equals("ACCEPTED")).count(),
                List.copyOf(decisions), tree(request), tree(response));
    }
}
