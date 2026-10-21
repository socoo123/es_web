package dev.esweb.travel;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.io.IOException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/attractions/changes")
public class ChangeController {
    public record Version(@NotNull @Min(0) Long seqNo, @NotNull @Min(1) Long primaryTerm) { }
    public record Replace(@NotNull @Min(0) Long seqNo, @NotNull @Min(1) Long primaryTerm,
            @NotNull @Valid ChangeDocument document) { }
    public record Patch(@NotNull @Min(0) Long seqNo, @NotNull @Min(1) Long primaryTerm,
            @Min(0) @Max(100000000) Integer ticketPriceFen, @Pattern(regexp = "open|closed") String status) {
        @AssertTrue public boolean isNonEmpty() { return ticketPriceFen != null || status != null; }
    }
    private final ChangeService service;
    public ChangeController(ChangeService service) { this.service = service; }
    @GetMapping("/{id}")
    public ChangeService.Read get(@PathVariable @Pattern(regexp = "[a-z0-9-]{1,60}") String id) throws IOException {
        return service.get(id);
    }
    @PostMapping("/{id}/create")
    public ChangeService.Written create(@PathVariable @Pattern(regexp = "[a-z0-9-]{1,60}") String id,
            @Valid @RequestBody ChangeDocument input) throws IOException { return service.create(id, input); }
    @PutMapping("/{id}")
    public ChangeService.Written replace(@PathVariable @Pattern(regexp = "[a-z0-9-]{1,60}") String id,
            @Valid @RequestBody Replace input) throws IOException { return service.replace(id, input); }
    @PatchMapping("/{id}")
    public ChangeService.Written patch(@PathVariable @Pattern(regexp = "[a-z0-9-]{1,60}") String id,
            @Valid @RequestBody Patch input) throws IOException { return service.patch(id, input); }
    @DeleteMapping("/{id}")
    public ChangeService.Written delete(@PathVariable @Pattern(regexp = "[a-z0-9-]{1,60}") String id,
            @Valid @RequestBody Version input) throws IOException { return service.delete(id, input); }
    @PostMapping("/refresh")
    public Object refresh() throws IOException { return service.refresh(); }
    @PostMapping("/pages/start")
    public PageResult start(@Valid @RequestBody PageInput input) throws IOException { return service.start(input); }
    @PostMapping("/pages/next")
    public PageResult next(@Valid @RequestBody PageController.Turn input) throws IOException { return service.next(input); }
    @PostMapping("/pages/close")
    public Object close(@Valid @RequestBody PageController.Close input) throws IOException { return service.close(input.cursor()); }
    @ExceptionHandler({ChangeService.ChangeFault.class})
    public ResponseEntity<ApiErrors.ErrorBody> fault(ChangeService.ChangeFault e) {
        return ResponseEntity.status(e.status).body(new ApiErrors.ErrorBody(e.code, e.getMessage()));
    }
    @ExceptionHandler(PageSearchService.PageFault.class)
    public ResponseEntity<ApiErrors.ErrorBody> pageFault(PageSearchService.PageFault e) {
        return ResponseEntity.status(e.status).body(new ApiErrors.ErrorBody(e.code, e.getMessage()));
    }
    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class,
            HandlerMethodValidationException.class})
    public ResponseEntity<ApiErrors.ErrorBody> invalid(Exception e) {
        return ResponseEntity.badRequest().body(new ApiErrors.ErrorBody("INVALID_CHANGE_INPUT",
                "请检查必填资料、整数分金额、open/closed状态、ID，以及读取到的seqNo/primaryTerm。"));
    }
}
