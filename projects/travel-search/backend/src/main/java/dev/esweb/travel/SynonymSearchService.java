package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch._types.query_dsl.TextQueryType;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.indices.AnalyzeRequest;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class SynonymSearchService {
    private static final String INDEX = "tut-f16-attractions";
    private final ElasticsearchClient client;
    private final JsonMapper json;
    public SynonymSearchService(ElasticsearchClient client, JsonMapper json) {
        this.client = client; this.json = json;
    }

    public record Token(String token, int position, int positionLength, int startOffset, int endOffset, String type) {}
    public record Card(String id, String name, String nameEn, List<String> aliases, String cityCode,
                       int ticketPriceFen, String currency, String status, Double score, List<Object> sortValues) {}
    public record Result(long total, String relation, long tookMs, SynonymInput conditions, String analyzer,
            JsonNode baseAnalysisRequest, JsonNode queryAnalysisRequest, JsonNode baseAnalysis, JsonNode queryAnalysis,
            List<Token> baseTokens, List<Token> queryTokens, JsonNode esRequest, List<Card> items) {}

    public String analyzer(SynonymInput input) {
        return switch (input.mode()) {
            case "plain" -> "travel_plain";
            case "aliases" -> "travel_base";
            case "late" -> "travel_late";
            case "graph", "phrase", "loose" -> "travel_search";
            default -> throw new IllegalArgumentException("Unknown synonym mode");
        };
    }

    public SearchRequest request(SynonymInput input) {
        boolean phrase = input.mode().equals("aliases") || input.mode().equals("phrase");
        List<String> fields = input.mode().equals("aliases")
                ? List.of("name", "name_en", "aliases") : List.of("name", "name_en");
        return SearchRequest.of(s -> s.index(INDEX).size(20).trackTotalHits(t -> t.enabled(true)).trackScores(true)
                .query(q -> q.bool(b -> b.must(m -> m.multiMatch(mm -> {
                    mm.query(input.q()).fields(fields).analyzer(analyzer(input))
                            .type(phrase ? TextQueryType.Phrase : TextQueryType.BestFields);
                    if (phrase) mm.slop(0);
                    else mm.operator(Operator.And).autoGenerateSynonymsPhraseQuery(!input.mode().equals("loose"));
                    return mm;
                }))
                        .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())))
                        .filter(f -> f.term(t -> t.field("status").value("open")))
                        .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                        .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                                .gte(0.0).lte(input.maxPriceFen().doubleValue()))))))
                .sort(srt -> srt.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    private List<Token> tokens(JsonNode response) {
        var filters = response.path("detail").path("tokenfilters");
        if (!filters.isArray() || filters.isEmpty()) throw new AttractionSearchService.IncompleteSearchException();
        var stream = filters.get(filters.size() - 1).path("tokens");
        if (!stream.isArray()) throw new AttractionSearchService.IncompleteSearchException();
        List<Token> result = new ArrayList<>();
        for (JsonNode t : stream) {
            if (!t.has("positionLength") || !t.has("token") || !t.has("position")
                    || !t.has("start_offset") || !t.has("end_offset") || !t.has("type"))
                throw new AttractionSearchService.IncompleteSearchException();
            result.add(new Token(t.get("token").asString(), t.get("position").asInt(), t.get("positionLength").asInt(),
                    t.get("start_offset").asInt(), t.get("end_offset").asInt(), t.get("type").asString()));
        }
        return List.copyOf(result);
    }

    public Result search(SynonymInput input) throws IOException {
        // Both analyses inspect supplied q. They do not read stored terms from existing documents.
        var base = AnalyzeRequest.of(a -> a.index(INDEX).analyzer("travel_base").text(input.q())
                .explain(true));
        var query = AnalyzeRequest.of(a -> a.index(INDEX).analyzer(analyzer(input)).text(input.q())
                .explain(true));
        var baseResponse = json.readTree(JsonpUtils.toJsonString(client.indices().analyze(base), client._jsonpMapper()));
        var queryResponse = json.readTree(JsonpUtils.toJsonString(client.indices().analyze(query), client._jsonpMapper()));
        var request = request(input);
        var response = client.search(request, SynonymAttraction.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0 || response.hits().total() == null)
            throw new AttractionSearchService.IncompleteSearchException();
        var cards = response.hits().hits().stream().map(hit -> {
            var source = hit.source();
            if (source == null || !hit.id().equals(source.attractionId()) || source.name() == null
                    || source.nameEn() == null || source.aliases() == null || source.ticketPriceFen() == null
                    || source.cityCode() == null || source.currency() == null || source.status() == null)
                throw new AttractionSearchService.IncompleteSearchException();
            List<Object> sort = hit.sort().stream().map(v -> (Object) v._get()).toList();
            return new Card(hit.id(), source.name(), source.nameEn(), source.aliases(), source.cityCode(),
                    source.ticketPriceFen(), source.currency(), source.status(), hit.score(), sort);
        }).toList();
        return new Result(response.hits().total().value(), response.hits().total().relation().jsonValue(), response.took(),
                input, analyzer(input), json.readTree(JsonpUtils.toJsonString(base, client._jsonpMapper())),
                json.readTree(JsonpUtils.toJsonString(query, client._jsonpMapper())), baseResponse, queryResponse,
                tokens(baseResponse), tokens(queryResponse), json.readTree(JsonpUtils.toJsonString(request, client._jsonpMapper())), cards);
    }
}
