package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class DictionaryController {
    private final DictionarySearchService service;
    public DictionaryController(DictionarySearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_DICTIONARY_INPUT",
                "请填写1至60个UTF-16单位的关键词、HZ/NJ城市、非负整数分预算和原索引/重建索引。"));
    }

    @PostMapping("/api/attractions/dictionary-search")
    public DictionarySearchService.Result search(@Valid @RequestBody DictionaryInput input) throws IOException {
        return service.search(input);
    }
}
