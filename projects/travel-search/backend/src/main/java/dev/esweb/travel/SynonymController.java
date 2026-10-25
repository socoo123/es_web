package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class SynonymController {
    private final SynonymSearchService service;
    public SynonymController(SynonymSearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_SYNONYM_INPUT",
                "请填写1至60个UTF-16单位的关键词、BJ/SY城市、非负整数分预算与本课六种观察模式。"));
    }

    @PostMapping("/api/attractions/synonym-search")
    public SynonymSearchService.Result search(@Valid @RequestBody SynonymInput input) throws IOException {
        return service.search(input);
    }
}
