package dev.esweb.travel;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public record SuggestAttraction(
        @JsonProperty("attraction_id") String attractionId, String name,
        @JsonProperty("name_sayt") String nameSayt, Map<String, Object> suggest,
        @JsonProperty("pinyin_full") String pinyinFull,
        @JsonProperty("pinyin_initials") String pinyinInitials,
        @JsonProperty("city_code") String cityCode,
        @JsonProperty("ticket_price_fen") Integer ticketPriceFen,
        String currency, String status) {
}
