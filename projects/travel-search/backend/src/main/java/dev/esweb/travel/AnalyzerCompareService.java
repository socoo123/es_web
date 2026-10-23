package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.indices.AnalyzeRequest;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class AnalyzerCompareService {
    private final ElasticsearchClient client;
    private final String index;
    private final JsonMapper json;

    public AnalyzerCompareService(ElasticsearchClient client,
            @Value("${travel.f14-index:tut-f14-attractions}") String index, JsonMapper json) {
        this.client = client; this.index = index; this.json = json;
    }

    public record Choice(String field, String analyzer) {}
    public record Result(long total, String relation, long tookMs, AnalyzerInput conditions,
            String field, String analyzer, String sampleText, JsonNode queryAnalysisRequest,
            JsonNode sampleAnalysisRequest, List<AnalysisSearchService.Token> queryTokens,
            List<AnalysisSearchService.Token> sampleTokens, JsonNode esRequest,
            List<AnalysisSearchService.Card> items) {}

    // Matches index-plugins.json; default is the independently usable built-in baseline.
    public Choice choice(AnalyzerInput input) {
        return switch (input.candidate()) {
            case "smartcn" -> new Choice("name.smartcn", "smartcn");
            case "icu" -> new Choice("name.icu", "icu_analyzer");
            case "ik-smart" -> new Choice("name.ik_smart", "ik_smart");
            case "ik-max" -> new Choice("name.ik_max", "ik_max_word");
            case "standard" -> new Choice("name", "standard");
            default -> throw new IllegalArgumentException("Unknown candidate");
        };
    }

    public SearchRequest request(AnalyzerInput input) {
        return SearchRequest.of(s -> s.index(index).size(20).trackTotalHits(t -> t.enabled(true)).trackScores(true)
                .query(q -> q.bool(b -> b.must(m -> m.match(t -> t.field(choice(input).field())
                                .query(input.q()).operator(Operator.And)))
                        .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())))
                        .filter(f -> f.term(t -> t.field("status").value("open")))
                        .filter(f -> f.term(t -> t.field("currency").value("CNY")))
                        .filter(f -> f.range(r -> r.number(n -> n.field("ticket_price_fen")
                                .gte(0.0).lte(input.maxPriceFen().doubleValue()))))))
                .sort(srt -> srt.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    public Result search(AnalyzerInput input) throws IOException {
        var selected = choice(input);
        String sample = switch (input.cityCode()) {
            case "NJ" -> "南京市长江大桥";
            case "SY" -> "沈阳故宫博物院";
            default -> input.q().equalsIgnoreCase("CAFE") ? "Ｃａｆｅ 城市咖啡馆" : "北京故宫博物院";
        };
        // Explicit analyzer makes an uninstalled plugin fail visibly, rather than reporting zero hits.
        var queryAnalysis = AnalyzeRequest.of(a -> a.index(index).analyzer(selected.analyzer()).text(input.q()));
        var sampleAnalysis = AnalyzeRequest.of(a -> a.index(index).analyzer(selected.analyzer()).text(sample));
        var queryTokens = client.indices().analyze(queryAnalysis).tokens().stream()
                .map(AnalysisSearchService.Token::from).toList();
        var sampleTokens = client.indices().analyze(sampleAnalysis).tokens().stream()
                .map(AnalysisSearchService.Token::from).toList();
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
                selected.field(), selected.analyzer(), sample,
                json.readTree(JsonpUtils.toJsonString(queryAnalysis, client._jsonpMapper())),
                json.readTree(JsonpUtils.toJsonString(sampleAnalysis, client._jsonpMapper())), queryTokens, sampleTokens,
                json.readTree(JsonpUtils.toJsonString(request, client._jsonpMapper())), cards);
    }
}
