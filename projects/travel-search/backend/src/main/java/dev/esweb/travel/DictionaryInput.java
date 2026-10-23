package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record DictionaryInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "HZ|NJ") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @Pattern(regexp = "original|rebuilt") String view) {
}
