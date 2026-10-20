package dev.esweb.travel;

import java.util.List;
import tools.jackson.databind.JsonNode;

public record SearchResult(long total, String totalRelation, long esTookMs,
                           SearchInput conditions, JsonNode esRequest, List<Card> items) {
    public record Card(String id, String name, String cityCode, Integer ticketPriceFen,
                       String currency, String status, Double score) {
    }
}
