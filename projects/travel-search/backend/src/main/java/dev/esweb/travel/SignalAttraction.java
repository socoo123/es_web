package dev.esweb.travel;

import com.fasterxml.jackson.annotation.JsonProperty;

public record SignalAttraction(
        @JsonProperty("attraction_id") String attractionId,
        String name, String description,
        @JsonProperty("city_code") String cityCode,
        @JsonProperty("ticket_price_fen") Integer ticketPriceFen,
        String currency, String status,
        @JsonProperty("review_avg") Double reviewAvg,
        @JsonProperty("review_count") Long reviewCount,
        @JsonProperty("quality_score") Double qualityScore,
        @JsonProperty("hot_30d") Double hot30d,
        @JsonProperty("quality_rank") Double qualityRank) {
}
