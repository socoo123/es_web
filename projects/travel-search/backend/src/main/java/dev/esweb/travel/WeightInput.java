package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record WeightInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "HZ|SZ") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @Pattern(regexp = "sum|best|tie|tuned|optional|required") String mode,
        @NotNull @Min(1) @Max(50) Integer nameWeight,
        @NotNull @Pattern(regexp = "hz-(exact|prefix|scatter|description|both|split|noise|photo|cruise|closed|expensive)|sz-exact") String explainId) {
}
