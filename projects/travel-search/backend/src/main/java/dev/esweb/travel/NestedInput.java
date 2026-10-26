package dev.esweb.travel;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
public record NestedInput(@NotNull @Pattern(regexp = "object|split|matched|unfiltered-sort|filtered-sort") String mode) {}
