package dev.esweb.travel;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

public record PageInput(@NotNull @Valid SortInput search,
        @NotNull @Min(1) @Max(5) Integer pageSize) { }
