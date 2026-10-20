package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.http.ResponseEntity;

@RestController
public class FacetController {
    private final FacetSearchService service;
    public FacetController(FacetSearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalidInput(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_SEARCH_INPUT",
                "请填写关键词、城市/主题数组和整数分预算；选项与金额须在本课允许范围内。"));
    }

    @PostMapping("/api/attractions/facet-search")
    public FacetResult search(@Valid @RequestBody FacetInput input) throws IOException {
        return service.search(input);
    }
}
