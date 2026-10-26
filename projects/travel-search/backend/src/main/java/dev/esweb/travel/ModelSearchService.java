package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.BoolQuery;
import co.elastic.clients.elasticsearch._types.query_dsl.ChildScoreMode;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonData;
import co.elastic.clients.json.JsonpSerializable;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.List;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class ModelSearchService {
    private final ElasticsearchClient client;
    private final JsonMapper json;
    public ModelSearchService(ElasticsearchClient client, JsonMapper json) {
        this.client = client; this.json = json;
    }
    public record Card(String id, JsonNode source) {}
    public record Result(String model, long total, String relation, long tookMs, ModelInput conditions,
                         JsonNode esRequest, JsonNode esResponse, List<Card> items) {}

    public String model(ModelInput input) {
        return switch (input.mode()) {
            case "hotel" -> "hotels";
            case "object" -> "object";
            case "nested" -> "nested";
            case "offers-flex", "offers-budget" -> "offers";
            default -> throw new IllegalArgumentException("validated mode required");
        };
    }
    public SearchRequest request(ModelInput input) {
        String model = model(input);
        Query query;
        if (model.equals("hotels")) {
            query = Query.of(q -> q.term(t -> t.field("hotel_id").value("h01")));
        } else if (model.equals("object")) {
            query = Query.of(q -> q.term(t -> t.field("rooms.room_id").value("r101")));
        } else if (model.equals("nested")) {
            query = Query.of(q -> q.nested(n -> n.path("rooms").scoreMode(ChildScoreMode.None)
                    .query(r -> r.term(t -> t.field("rooms.room_id").value("r101")))));
        } else {
            var filters = new BoolQuery.Builder()
                    .filter(f -> f.term(t -> t.field("city_code").value("HZ")))
                    .filter(f -> f.term(t -> t.field("hotel_status").value("open")))
                    .filter(f -> f.term(t -> t.field("offer_status").value("active")))
                    .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                    .filter(f -> f.term(t -> t.field("service_date").value("2026-11-01")));
            boolean flex = input.mode().equals("offers-flex");
            if (flex) filters
                    .filter(f -> f.term(t -> t.field("bed_type").value("twin")))
                    .filter(f -> f.term(t -> t.field("meal").value("breakfast")))
                    .filter(f -> f.term(t -> t.field("cancellation").value("flexible")));
            filters.filter(f -> f.range(r -> r.number(n -> n.field("price_minor")
                    .gte(0.0).lte(flex ? 70000.0 : 55000.0))));
            if (flex) filters.filter(f -> f.range(r -> r.number(n -> n.field("capacity").gte(2.0))));
            query = Query.of(q -> q.bool(filters.build()));
        }
        String sortField = model.equals("offers") ? "offer_id" : "hotel_id";
        return SearchRequest.of(s -> s.index("tut-f23-" + model).size(20)
                .trackTotalHits(t -> t.enabled(true)).query(query)
                .sort(so -> so.field(f -> f.field(sortField).order(SortOrder.Asc))));
    }
    private JsonNode tree(JsonpSerializable value) {
        return json.readTree(JsonpUtils.toJsonString(value, client._jsonpMapper()));
    }
    private boolean text(JsonNode source, String field) {
        return source.hasNonNull(field) && source.get(field).isString() && !source.get(field).asString().isBlank();
    }
    private void validateSource(String model, String id, JsonNode source) {
        if (source == null || !text(source, "hotel_id") || !text(source, "hotel_name")
                || !text(source, "city_code") || !text(source, "hotel_status"))
            throw new AttractionSearchService.IncompleteSearchException();
        if (!model.equals("offers")) {
            if (!id.equals(source.get("hotel_id").asString()))
                throw new AttractionSearchService.IncompleteSearchException();
            if (!model.equals("hotels") && (!source.hasNonNull("rooms") || !source.get("rooms").isArray()
                    || source.get("rooms").isEmpty()))
                throw new AttractionSearchService.IncompleteSearchException();
            if (!model.equals("hotels")) for (JsonNode room : source.get("rooms")) {
                if (!text(room, "room_id") || !text(room, "room_name") || !text(room, "bed_type")
                        || !room.hasNonNull("capacity") || !room.get("capacity").isIntegralNumber()
                        || room.get("capacity").asInt() < 1 || !room.hasNonNull("rates")
                        || !room.get("rates").isArray() || room.get("rates").isEmpty())
                    throw new AttractionSearchService.IncompleteSearchException();
                for (JsonNode rate : room.get("rates")) {
                    if (!text(rate, "offer_id") || !text(rate, "rate_plan_id") || !text(rate, "currency")
                            || !text(rate, "offer_status") || !text(rate, "meal") || !text(rate, "cancellation")
                            || !text(rate, "service_date") || !text(rate, "snapshot_at")
                            || !rate.hasNonNull("price_minor") || !rate.get("price_minor").isIntegralNumber()
                            || rate.get("price_minor").asLong() < 0)
                        throw new AttractionSearchService.IncompleteSearchException();
                }
            }
        } else {
            for (String field : List.of("offer_id", "room_id", "room_name", "bed_type", "rate_plan_id", "service_date",
                    "meal", "cancellation", "currency", "offer_status", "snapshot_at")) {
                if (!text(source, field)) throw new AttractionSearchService.IncompleteSearchException();
            }
            if (!id.equals(source.get("offer_id").asString()) || !source.hasNonNull("price_minor")
                    || !source.get("price_minor").isIntegralNumber() || source.get("price_minor").asLong() < 0
                    || !source.hasNonNull("capacity") || !source.get("capacity").isIntegralNumber()
                    || source.get("capacity").asInt() < 1)
                throw new AttractionSearchService.IncompleteSearchException();
        }
    }
    public Result inspect(ModelInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, JsonData.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0
                || response.hits().total() == null || !response.hits().total().relation().jsonValue().equals("eq"))
            throw new AttractionSearchService.IncompleteSearchException();
        String model = model(input);
        List<Card> cards = response.hits().hits().stream().map(hit -> {
            JsonNode source = hit.source() == null ? null : json.readTree(hit.source().toJson().toString());
            validateSource(model, hit.id(), source);
            if (model.equals("offers") && (!"HZ".equals(source.get("city_code").asString())
                    || !"open".equals(source.get("hotel_status").asString())
                    || !"active".equals(source.get("offer_status").asString())
                    || !"CNY".equals(source.get("currency").asString())
                    || !"2026-11-01".equals(source.get("service_date").asString())
                    || source.get("price_minor").asLong() > (input.mode().equals("offers-flex") ? 70000 : 55000)))
                throw new AttractionSearchService.IncompleteSearchException();
            if (model.equals("offers") && input.mode().equals("offers-flex")
                    && (!"twin".equals(source.get("bed_type").asString())
                    || !"breakfast".equals(source.get("meal").asString())
                    || !"flexible".equals(source.get("cancellation").asString())
                    || source.get("capacity").asInt() < 2))
                throw new AttractionSearchService.IncompleteSearchException();
            if (hit.sort().size() != 1) throw new AttractionSearchService.IncompleteSearchException();
            return new Card(hit.id(), source);
        }).toList();
        return new Result(model, response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), input, tree(request), tree(response), cards);
    }
}
