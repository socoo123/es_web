package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class SuggestController {
    private final SuggestSearchService service;
    public SuggestController(SuggestSearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_SUGGEST_INPUT",
                "请填1至60个UTF-16单位的关键词、BJ/SY城市与本课六种模式；拼音只收2至40个英文字母。"));
    }

    @PostMapping("/api/attractions/suggestions")
    public SuggestSearchService.Result search(@Valid @RequestBody SuggestInput input) throws IOException {
        return service.search(input);
    }
}
