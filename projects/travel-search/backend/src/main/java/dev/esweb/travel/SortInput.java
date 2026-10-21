package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record SortInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "ALL|HZ|FZ|SH") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @Pattern(regexp = "relevance|price|distance") String sortMode,
        @NotNull @DecimalMin("-90") @DecimalMax("90") Double latitude,
        @NotNull @DecimalMin("-180") @DecimalMax("180") Double longitude,
        @NotNull Boolean trackScores) {
}
