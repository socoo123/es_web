package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class ScoreController {
    private final ScoreSearchService service;
    public ScoreController(ScoreSearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_SCORE_INPUT",
                "请填写1至60字符关键词、HZ或SZ城市、非负整数分预算，并选择页面列出的模式与解释ID。"));
    }

    @PostMapping("/api/attractions/score-search")
    public ScoreSearchService.Result search(@Valid @RequestBody ScoreInput input) throws IOException {
        return service.search(input);
    }
}
