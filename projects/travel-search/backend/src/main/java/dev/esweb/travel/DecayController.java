package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class DecayController {
    private final DecaySearchService service;
    public DecayController(DecaySearchService service) { this.service = service; }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_DECAY_INPUT",
                "请填写1至60字符关键词、HZ或SZ、非负整数分预算、有效经纬度、可空且大于0至100km半径，并选择列出的评分/排序模式与解释ID。"));
    }

    @PostMapping("/api/attractions/decay-search")
    public DecaySearchService.Result search(@Valid @RequestBody DecayInput input) throws IOException {
        return service.search(input);
    }
}
