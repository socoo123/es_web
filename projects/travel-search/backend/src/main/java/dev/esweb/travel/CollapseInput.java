package dev.esweb.travel;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public record CollapseInput(@NotNull @Pattern(regexp="all|top-offers|top-hotels") String mode) {}
