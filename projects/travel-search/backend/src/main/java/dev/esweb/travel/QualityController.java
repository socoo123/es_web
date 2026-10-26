package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class QualityController {
    private final QualityEvaluationService service;
    public QualityController(QualityEvaluationService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_QUALITY_INPUT",
                "请选择adjust、holdout或assessment查询集，以及baseline或candidate策略。"));
    }

    @PostMapping("/api/quality/evaluate")
    public QualityEvaluationService.Result evaluate(@Valid @RequestBody QualityInput input) throws IOException {
        return service.evaluate(input);
    }
}
