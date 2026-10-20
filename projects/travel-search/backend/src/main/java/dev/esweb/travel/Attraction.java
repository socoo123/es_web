package dev.esweb.travel;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record Attraction(
        @JsonProperty("attraction_id") String attractionId,
        String name,
        @JsonProperty("city_code") String cityCode,
        @JsonProperty("ticket_price_fen") Integer ticketPriceFen,
        String currency,
        String status) {
}
