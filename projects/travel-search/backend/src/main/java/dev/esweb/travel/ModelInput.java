package dev.esweb.travel;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public record ModelInput(@NotNull @Pattern(regexp = "hotel|object|nested|offers-flex|offers-budget") String mode) {}
