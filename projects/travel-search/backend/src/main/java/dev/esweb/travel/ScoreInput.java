package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record ScoreInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "HZ|SZ") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @Pattern(regexp = "scored|filtered|city-scored") String mode,
        @NotNull @Pattern(regexp = "hz-(short|once|twice|four|long|night|closed|other|missing)|sz-copy") String explainId) {
}
