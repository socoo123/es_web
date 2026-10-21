package dev.esweb.travel;

import java.util.List;
import tools.jackson.databind.JsonNode;

public record SortResult(long total, String totalRelation, long tookMs, SortInput conditions,
        JsonNode esRequest, List<Card> items) {
    public record Card(String id, String name, String cityCode, Integer ticketPriceFen,
            String currency, String status, Double score, List<Object> sortValues,
            boolean hasLocation, Double distanceKm) { }
}
