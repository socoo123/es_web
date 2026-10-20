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
    private final MultiFieldSearchService multiSearch;

    public SearchController(AttractionSearchService search, MultiFieldSearchService multiSearch) {
        this.search = search;
        this.multiSearch = multiSearch;
    }

    @GetMapping("/api/health")
    public Map<String, String> health() {
        return Map.of("application", "up", "scope", "java-process-only");
    }

    @PostMapping("/api/attractions/multi-search")
    public MultiFieldResult multiSearch(@Valid @RequestBody SearchInput input) throws IOException {
        return multiSearch.search(input);
    }

    @PostMapping("/api/attractions/search")
    public SearchResult search(@Valid @RequestBody SearchInput input) throws IOException {
        return search.search(input);
    }
}
