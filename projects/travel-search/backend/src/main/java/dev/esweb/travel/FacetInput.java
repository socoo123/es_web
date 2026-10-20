package dev.esweb.travel;

import jakarta.validation.constraints.*;
import java.util.List;

public record FacetInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Size(max = 3) List<@NotNull @Pattern(regexp = "HZ|FZ|SH") String> cityCodes,
        @NotNull @Size(max = 4) List<@NotNull @Pattern(regexp = "lake|walk|garden|culture") String> themes,
        @NotNull @Min(0) @Max(100000000) Integer maxPriceFen) {
}
