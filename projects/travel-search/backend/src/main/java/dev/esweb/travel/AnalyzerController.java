package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class AnalyzerController {
    private final AnalyzerCompareService service;
    public AnalyzerController(AnalyzerCompareService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_ANALYZER_INPUT",
                "请填写1至60个UTF-16单位的关键词、BJ/NJ/SY城市、非负整数分预算和页面列出的方案。"));
    }

    @PostMapping("/api/attractions/analyzer-search")
    public AnalyzerCompareService.Result search(@Valid @RequestBody AnalyzerInput input) throws IOException {
        return service.search(input);
    }
}
