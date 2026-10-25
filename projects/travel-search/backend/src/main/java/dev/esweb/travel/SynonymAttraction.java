package dev.esweb.travel;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record SynonymAttraction(
        @JsonProperty("attraction_id") String attractionId,
        String name,
        @JsonProperty("name_en") String nameEn,
        List<String> aliases,
        @JsonProperty("city_code") String cityCode,
        @JsonProperty("ticket_price_fen") Integer ticketPriceFen,
        String currency, String status) {
}
