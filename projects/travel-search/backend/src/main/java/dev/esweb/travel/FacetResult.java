package dev.esweb.travel;

import java.util.List;
import tools.jackson.databind.JsonNode;

public record FacetResult(long total, String totalRelation, long esTookMs,
                          FacetInput conditions, JsonNode esRequest, List<Card> items,
                          TermsFacet cities, TermsFacet themes, long missingThemeCount,
                          long priceScopeTotal, List<RangeBucket> prices) {
    public record Bucket(String key, long docCount, long docCountErrorUpperBound) {}
    public record TermsFacet(String scope, long scopeTotal, long docCountErrorUpperBound,
                             long sumOtherDocCount, List<Bucket> buckets) {}
    public record RangeBucket(String key, Double fromFen, Double toFen, long docCount) {}
    public record Card(String id, String name, String cityCode, Integer ticketPriceFen,
                       String currency, String status, List<String> themes) {}
}
