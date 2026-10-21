package dev.esweb.travel;

import com.fasterxml.jackson.annotation.JsonProperty;

public record SortAttraction(
        @JsonProperty("attraction_id") String attractionId,
        String name,
        @JsonProperty("city_code") String cityCode,
        @JsonProperty("ticket_price_fen") Integer ticketPriceFen,
        String currency, String status, Location location) {
    public record Location(Double lat, Double lon) { }
}
