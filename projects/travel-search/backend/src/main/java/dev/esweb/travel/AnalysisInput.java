package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record AnalysisInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "BJ|SY") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @Pattern(regexp = "mismatch|aligned|phrase|case-sensitive") String mode) {
}
