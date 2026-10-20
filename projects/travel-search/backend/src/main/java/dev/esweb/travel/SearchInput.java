package dev.esweb.travel;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record SearchInput(
        @NotBlank @Size(max = 60) String q,
        @NotBlank @Pattern(regexp = "[A-Z]{2}") String cityCode,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen,
        @NotNull @DecimalMin("-90") @DecimalMax("90") Double latitude,
        @NotNull @DecimalMin("-180") @DecimalMax("180") Double longitude,
        @NotNull @DecimalMin(value = "0", inclusive = false) @DecimalMax("100") Double radiusKm) {
}
