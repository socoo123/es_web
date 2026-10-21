package dev.esweb.travel;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/attractions/pages")
public class PageController {
    public record Turn(@NotBlank String cursor, @NotNull @Min(1) Integer afterPage,
            @NotNull @Valid PageInput conditions) { }
    public record Close(@NotBlank String cursor) { }
    private final PageSearchService service;
    public PageController(PageSearchService service) { this.service = service; }

    @PostMapping("/start")
    public PageResult start(@Valid @RequestBody PageInput input) throws IOException {
        return service.start(input);
    }
    @PostMapping("/next")
    public PageResult next(@Valid @RequestBody Turn input) throws IOException {
        return service.next(input);
    }
    @PostMapping("/close")
    public Object close(@Valid @RequestBody Close input) throws IOException {
        return service.close(input.cursor());
    }
    @ExceptionHandler(PageSearchService.PageFault.class)
    public ResponseEntity<ApiErrors.ErrorBody> fault(PageSearchService.PageFault error) {
        return ResponseEntity.status(error.status).body(new ApiErrors.ErrorBody(error.code, error.getMessage()));
    }
}
