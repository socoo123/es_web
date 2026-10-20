package dev.esweb.travel;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HealthController {
    public record HealthResponse(String status, String service, String stage) {}

    @GetMapping("/api/health")
    public HealthResponse health() {
        return new HealthResponse("UP", "travel-portal", "F01");
    }
}
