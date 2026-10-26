package dev.esweb.travel;

import com.fasterxml.jackson.annotation.JsonProperty;

public record QualityAttraction(
        @JsonProperty("attraction_id") String attractionId,
        String name, String description,
        @JsonProperty("city_code") String cityCode,
        String status, String currency,
        @JsonProperty("ticket_price_fen") Integer ticketPriceFen) {}
