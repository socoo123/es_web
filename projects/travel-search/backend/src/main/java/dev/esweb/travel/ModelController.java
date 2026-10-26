package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class ModelController {
    private final ModelSearchService service;
    public ModelController(ModelSearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_MODEL_INPUT",
                "请选择hotel、object、nested、offers-flex或offers-budget固定案例。"));
    }

    @PostMapping("/api/model/inspect")
    public ModelSearchService.Result inspect(@Valid @RequestBody ModelInput input) throws IOException {
        return service.inspect(input);
    }
}
