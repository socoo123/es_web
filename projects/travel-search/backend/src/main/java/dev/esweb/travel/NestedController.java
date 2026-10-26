package dev.esweb.travel;
import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
@RestController
public class NestedController {
    private final NestedSearchService service;
    public NestedController(NestedSearchService service) { this.service = service; }
    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_NESTED_INPUT",
                "请选择object、split、matched、unfiltered-sort或filtered-sort固定案例。"));
    }
    @PostMapping("/api/nested/inspect")
    public NestedSearchService.Result inspect(@Valid @RequestBody NestedInput input) throws IOException {
        return service.inspect(input);
    }
}
