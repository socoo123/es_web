package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class WeightController {
    private final WeightSearchService service;
    public WeightController(WeightSearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_WEIGHT_INPUT",
                "请填写1至60字符关键词、HZ或SZ、非负整数分预算、1至50整数名称权重，并选择列出的模式与解释ID。"));
    }

    @PostMapping("/api/attractions/weight-search")
    public WeightSearchService.Result search(@Valid @RequestBody WeightInput input) throws IOException {
        return service.search(input);
    }
}
