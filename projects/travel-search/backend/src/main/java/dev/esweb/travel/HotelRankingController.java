package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestController
public class HotelRankingController {
    private final HotelRankingService service;
    public HotelRankingController(HotelRankingService service) { this.service=service; }
    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception error) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_HOTEL_RANKING_INPUT",
                "请检查关键词、酒店/房型排序、两个布尔硬条件和候选范围；本课日期/人数固定。"));
    }
    @PostMapping("/api/hotel-ranking/inspect")
    public HotelRankingService.Result inspect(@Valid @RequestBody HotelRankingInput input) throws IOException {
        return service.inspect(input);
    }
}
