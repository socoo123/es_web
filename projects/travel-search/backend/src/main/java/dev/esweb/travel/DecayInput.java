package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record DecayInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "HZ|SZ") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @DecimalMin("-90") @DecimalMax("90") Double latitude,
        @NotNull @DecimalMin("-180") @DecimalMax("180") Double longitude,
        @DecimalMin(value = "0", inclusive = false) @DecimalMax("100") Double radiusKm,
        @NotNull @Pattern(regexp = "text|bare|sum|product|multiply|replace") String mode,
        @NotNull @Pattern(regexp = "relevance|price|distance") String sortMode,
        @NotNull @Pattern(regexp = "hz-(far|near|fresh|stale|missing|no-date|no-geo|weak|noise|closed|expensive|extreme|future)|sz-near") String explainId) {
}
