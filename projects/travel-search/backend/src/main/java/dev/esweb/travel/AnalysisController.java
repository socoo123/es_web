package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class AnalysisController {
    private final AnalysisSearchService service;
    public AnalysisController(AnalysisSearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_ANALYSIS_INPUT",
                "请填写1至60字符关键词、BJ或SY城市、非负整数分预算，以及页面列出的分析模式。"));
    }

    @PostMapping("/api/attractions/analysis-search")
    public AnalysisSearchService.Result search(@Valid @RequestBody AnalysisInput input) throws IOException {
        return service.search(input);
    }
}
