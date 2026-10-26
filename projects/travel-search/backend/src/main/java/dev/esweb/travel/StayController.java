package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class StayController {
    private final StaySearchService service;
    public StayController(StaySearchService service) { this.service = service; }
    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class, IllegalArgumentException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_STAY_INPUT",
                "日期须在2026-11-01至04内且入住早于离店；房间1–3，每间成人1–4，总预算为1–2000000整数分。"));
    }
    @PostMapping("/api/stay/inspect")
    public StaySearchService.Result inspect(@Valid @RequestBody StayInput input) throws IOException {
        input.validateDates(); return service.inspect(input);
    }
}
