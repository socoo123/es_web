package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.indices.AnalyzeRequest;
import co.elastic.clients.elasticsearch.indices.analyze.AnalyzeToken;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class AnalysisSearchService {
    private final ElasticsearchClient client;
    private final String index;
    private final JsonMapper json;

    public AnalysisSearchService(ElasticsearchClient client,
            @Value("${travel.f13-index:tut-f13-attractions}") String index, JsonMapper json) {
        this.client = client;
        this.index = index;
        this.json = json;
    }

    public record Token(String token, long position, long startOffset, long endOffset, String type) {
        static Token from(AnalyzeToken token) {
            return new Token(token.token(), token.position(), token.startOffset(), token.endOffset(), token.type());
        }
    }
    public record Card(String id, String name, String cityCode, int ticketPriceFen,
                       Double score, List<Object> sortValues) {}
    public record Result(long total, String relation, long tookMs, AnalysisInput conditions,
                         String field, String searchAnalyzer, JsonNode indexAnalysisRequest,
                         JsonNode searchAnalysisRequest, List<Token> indexTokens, List<Token> searchTokens,
                         JsonNode esRequest, List<Card> items) {}

    // These choices match search/f13/index.json. No arbitrary field/analyzer/index from the browser.
    public String field(AnalysisInput input) {
        return input.mode().equals("mismatch") ? "name.mismatch" : "name";
    }
    public String searchAnalyzer(AnalysisInput input) {
        return switch (input.mode()) {
            case "mismatch" -> "keyword";
            case "case-sensitive" -> "case_sensitive";
            default -> "travel_text";
        };
    }

    public SearchRequest request(AnalysisInput input) {
        String field = field(input);
        Query text = input.mode().equals("phrase")
                ? Query.of(q -> q.matchPhrase(m -> m.field(field).query(input.q()).slop(0)))
                : Query.of(q -> q.match(m -> {
                    m.field(field).query(input.q()).operator(Operator.And);
                    if (input.mode().equals("case-sensitive")) m.analyzer("case_sensitive");
                    return m;
                }));
        return SearchRequest.of(s -> s.index(index).size(20).trackTotalHits(t -> t.enabled(true)).trackScores(true)
                .query(q -> q.bool(b -> b.must(text)
                        .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())))
                        .filter(f -> f.term(t -> t.field("status").value("open")))
                        .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                        .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                                .gte(0.0).lte(input.maxPriceFen().doubleValue()))))))
                .sort(srt -> srt.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    public Result search(AnalysisInput input) throws IOException {
        // Both analyze calls inspect the supplied q, not stored postings from an existing document.
        var indexRequest = AnalyzeRequest.of(a -> a.index(index).field(field(input)).text(input.q()));
        var searchRequest = AnalyzeRequest.of(a -> a.index(index).analyzer(searchAnalyzer(input)).text(input.q()));
        var indexTokens = client.indices().analyze(indexRequest).tokens().stream().map(Token::from).toList();
        var searchTokens = client.indices().analyze(searchRequest).tokens().stream().map(Token::from).toList();
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
            return new Card(hit.id(), source.name(), source.cityCode(), source.ticketPriceFen(), hit.score(), sort);
        }).toList();
        return new Result(response.hits().total().value(), response.hits().total().relation().jsonValue(),
                response.took(), input, field(input), searchAnalyzer(input),
                json.readTree(JsonpUtils.toJsonString(indexRequest, client._jsonpMapper())),
                json.readTree(JsonpUtils.toJsonString(searchRequest, client._jsonpMapper())),
                indexTokens, searchTokens, json.readTree(JsonpUtils.toJsonString(request, client._jsonpMapper())), cards);
    }
}
