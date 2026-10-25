package dev.esweb.travel;

import jakarta.validation.constraints.*;

public record SynonymInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "BJ|SY") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @Pattern(regexp = "plain|aliases|graph|phrase|loose|late") String mode) {
}
