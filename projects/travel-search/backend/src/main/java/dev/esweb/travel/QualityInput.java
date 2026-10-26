package dev.esweb.travel;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public record QualityInput(
        @NotNull @Pattern(regexp = "adjust|holdout|assessment") String split,
        @NotNull @Pattern(regexp = "baseline|candidate") String strategy) {}
