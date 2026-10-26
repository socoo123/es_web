package dev.esweb.travel;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;

public record StayInput(@NotNull LocalDate checkIn, @NotNull LocalDate checkOut,
        @NotNull @Min(1) @Max(3) Integer rooms,
        @NotNull @Min(1) @Max(4) Integer adultsPerRoom,
        @NotNull @Min(1) @Max(2000000) Long budgetMinor) {
    public void validateDates() {
        if (checkIn.isBefore(LocalDate.of(2026,11,1)) || checkOut.isAfter(LocalDate.of(2026,11,4))
                || !checkIn.isBefore(checkOut)) throw new IllegalArgumentException("Unsupported stay interval");
    }
}
