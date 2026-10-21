package dev.esweb.travel;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.List;

public record ChangeDocument(
        @NotBlank @Pattern(regexp = "[a-z0-9-]{1,60}") @JsonProperty("attraction_id") String attractionId,
        @NotBlank @Size(max = 100) String name,
        @NotNull @Size(max = 10) List<@NotBlank @Size(max = 100) String> aliases,
        @NotBlank @Size(max = 1000) String description,
        @NotNull @Pattern(regexp = "HZ|FZ|SH") @JsonProperty("city_code") String cityCode,
        @NotNull @Min(0) @Max(100000000) @JsonProperty("ticket_price_fen") Integer ticketPriceFen,
        @NotNull @Pattern(regexp = "CNY|USD") String currency,
        @NotNull @Pattern(regexp = "open|closed") String status,
        @NotNull @Valid Location location) {
    public record Location(@NotNull @DecimalMin("-90") @DecimalMax("90") Double lat,
            @NotNull @DecimalMin("-180") @DecimalMax("180") Double lon) { }
}
