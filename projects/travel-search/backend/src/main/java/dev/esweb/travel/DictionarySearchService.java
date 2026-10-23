package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.core.TermvectorsRequest;
import co.elastic.clients.elasticsearch.indices.AnalyzeRequest;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.Comparator;
import java.util.List;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class DictionarySearchService {
    private final ElasticsearchClient client;
    private final JsonMapper json;
    public DictionarySearchService(ElasticsearchClient client, JsonMapper json) {
        this.client = client; this.json = json;
    }

    public record StoredToken(String token, int position, int startOffset, int endOffset) {}
    public record Result(long total, String relation, long tookMs, DictionaryInput conditions,
            String index, String exampleId, JsonNode queryAnalysisRequest, JsonNode storedVectorRequest,
            List<AnalysisSearchService.Token> queryTokens, List<StoredToken> storedTokens,
            JsonNode storedVectors, JsonNode esRequest, List<AnalysisSearchService.Card> items) {}

    public String index(DictionaryInput input) {
        return switch (input.view()) {
            case "original" -> "tut-f15-v1";
            case "rebuilt" -> "tut-f15-v2";
            default -> throw new IllegalArgumentException("Unknown dictionary view");
        };
    }

    public SearchRequest request(DictionaryInput input) {
        return SearchRequest.of(s -> s.index(index(input)).size(20).trackTotalHits(t -> t.enabled(true)).trackScores(true)
                .query(q -> q.bool(b -> b.must(m -> m.match(t -> t.field("name")
                                .query(input.q()).operator(Operator.And)))
                        .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())))
                        .filter(f -> f.term(t -> t.field("status").value("open")))
                        .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                        .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                                .gte(0.0).lte(input.maxPriceFen().doubleValue()))))))
                .sort(srt -> srt.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    public Result search(DictionaryInput input) throws IOException {
        String index = index(input);
        // Fixed old document: not a current re-analysis of its _source.
        String example = input.cityCode().equals("HZ") ? "hz-brand" : "nj-bay";
        var analysis = AnalyzeRequest.of(a -> a.index(index).analyzer("ik_smart").text(input.q()));
        var vectorRequest = TermvectorsRequest.of(t -> t.index(index).id(example).fields("name")
                .positions(true).offsets(true).termStatistics(false).fieldStatistics(false));
        var queryTokens = client.indices().analyze(analysis).tokens().stream()
                .map(AnalysisSearchService.Token::from).toList();
        var vectors = client.termvectors(vectorRequest);
        var field = vectors.termVectors().get("name");
        if (!vectors.found() || field == null)
            throw new AttractionSearchService.IncompleteSearchException();
        var stored = field.terms().entrySet().stream().flatMap(entry -> entry.getValue().tokens().stream().map(t -> {
            if (t.startOffset() == null || t.endOffset() == null)
                throw new AttractionSearchService.IncompleteSearchException();
            return new StoredToken(entry.getKey(), t.position(), t.startOffset(), t.endOffset());
        })).sorted(Comparator.comparingInt(StoredToken::position).thenComparing(StoredToken::token)).toList();
        var request = request(input);
        var response = client.search(request, Attraction.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0 || response.hits().total() == null)
            throw new AttractionSearchService.IncompleteSearchException();
        var cards = response.hits().hits().stream().map(hit -> {
            var source = hit.source();
            if (source == null || !hit.id().equals(source.attractionId()) || source.name() == null
                    || source.ticketPriceFen() == null || source.cityCode() == null)
                throw new AttractionSearchService.IncompleteSearchException();
            List<Object> sort = hit.sort().stream().map(v -> (Object) v._get()).toList();
            return new AnalysisSearchService.Card(hit.id(), source.name(), source.cityCode(), source.ticketPriceFen(), hit.score(), sort);
        }).toList();
        return new Result(response.hits().total().value(), response.hits().total().relation().jsonValue(), response.took(), input,
                index, example, json.readTree(JsonpUtils.toJsonString(analysis, client._jsonpMapper())),
                json.readTree(JsonpUtils.toJsonString(vectorRequest, client._jsonpMapper())), queryTokens, stored,
                json.readTree(JsonpUtils.toJsonString(vectors, client._jsonpMapper())),
                json.readTree(JsonpUtils.toJsonString(request, client._jsonpMapper())), cards);
    }
}
