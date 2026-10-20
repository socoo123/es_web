package dev.esweb.travel;

import jakarta.validation.Valid;
import java.io.IOException;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class SearchController {
    private final AttractionSearchService search;

    public SearchController(AttractionSearchService search) {
        this.search = search;
    }

    @GetMapping("/api/health")
    public Map<String, String> health() {
        return Map.of("application", "up", "scope", "java-process-only");
    }

    @PostMapping("/api/attractions/search")
    public SearchResult search(@Valid @RequestBody SearchInput input) throws IOException {
        return search.search(input);
    }
}
