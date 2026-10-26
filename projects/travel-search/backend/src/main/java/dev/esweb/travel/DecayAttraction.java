package dev.esweb.travel;

import com.fasterxml.jackson.annotation.JsonProperty;

public record DecayAttraction(
        @JsonProperty("attraction_id") String attractionId,
        String name, String description,
        @JsonProperty("city_code") String cityCode,
        @JsonProperty("ticket_price_fen") Integer ticketPriceFen,
        String currency, String status, SortAttraction.Location location,
        @JsonProperty("verified_at") String verifiedAt) {
}
