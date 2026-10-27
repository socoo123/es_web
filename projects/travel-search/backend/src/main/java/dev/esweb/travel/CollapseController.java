package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class CollapseController {
    private final CollapseSearchService service;
    public CollapseController(CollapseSearchService service) { this.service = service; }
    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_COLLAPSE_INPUT",
                "mode只能是top-offers、top-hotels或all；日期/房间/人数固定，先选择观察范围。"));
    }
    @PostMapping("/api/collapse/inspect")
    public CollapseSearchService.Result inspect(@Valid @RequestBody CollapseInput input) throws IOException {
        return service.inspect(input);
    }
}
