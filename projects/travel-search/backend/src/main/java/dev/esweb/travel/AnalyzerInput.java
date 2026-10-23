package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record AnalyzerInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "BJ|NJ|SY") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @Pattern(regexp = "standard|smartcn|icu|ik-smart|ik-max") String candidate) {
}
