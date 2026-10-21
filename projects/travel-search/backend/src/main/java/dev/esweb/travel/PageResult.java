package dev.esweb.travel;

import java.util.List;
import tools.jackson.databind.JsonNode;

public record PageResult(String cursor, int pageNumber, boolean hasNext, long total,
        String totalRelation, PageInput conditions, JsonNode esRequest, List<Card> items) {
    public record Card(String id, String name, Integer ticketPriceFen, Double score,
            List<Object> sortValues) { }
}
