package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.http.ResponseEntity;

@RestController
public class SortController {
    private final SortSearchService service;
    public SortController(SortSearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalidInput(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_SEARCH_INPUT",
                "请检查关键词、城市、整数分预算、排序模式、坐标与评分开关；所有字段必填。"));
    }

    @PostMapping("/api/attractions/sort-search")
    public SortResult search(@Valid @RequestBody SortInput input) throws IOException {
        return service.search(input);
    }
}
