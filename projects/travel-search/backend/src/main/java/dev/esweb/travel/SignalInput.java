package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record SignalInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "HZ|SZ") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @Pattern(regexp = "text|raw|average|quality|compressed|bounded|rank|rank-only") String mode,
        @NotNull @Pattern(regexp = "hz-(small|steady|fresh|zero|missing|huge|hot|noise|closed|expensive)|sz-steady") String explainId) {
}
