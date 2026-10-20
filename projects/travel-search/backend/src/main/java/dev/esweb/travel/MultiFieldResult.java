package dev.esweb.travel;

import java.util.List;
import tools.jackson.databind.JsonNode;

public record MultiFieldResult(long total, String totalRelation, long esTookMs,
                               SearchInput conditions, JsonNode esRequest, List<Card> items) {
    public record Segment(String text, boolean matched) {
    }
    public record Snippet(String field, boolean highlighted, List<Segment> segments) {
    }
    public record Card(String id, String name, String cityCode, Integer ticketPriceFen,
                       String currency, String status, Double score, List<Snippet> snippets) {
    }
}
