package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.Operator;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import co.elastic.clients.elasticsearch._types.query_dsl.TextQueryType;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.core.search.CompletionContext;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class SuggestSearchService {
    private static final String INDEX = "tut-f17-attractions";
    private final ElasticsearchClient client;
    private final JsonMapper json;
    public SuggestSearchService(ElasticsearchClient client, JsonMapper json) {
        this.client = client; this.json = json;
    }

    public record Card(String id, String name, String pinyinFull, String pinyinInitials, String cityCode,
            int ticketPriceFen, String currency, String status, Double score, String suggestionText, List<Object> sortValues) {}
    public record Result(SuggestInput conditions, String normalizedQ, int candidateLimit, int rawCandidateCount,
            int returnedCount, Long total, String relation, long tookMs, String deduplication,
            JsonNode esRequest, JsonNode esResponse, List<Card> items) {}

    public String normalized(SuggestInput input) { return input.q().strip().toLowerCase(Locale.ROOT); }

    public SearchRequest request(SuggestInput input) {
        String q = normalized(input);
        if (input.mode().equals("completion")) {
            var scope = CompletionContext.of(c -> c.context(v -> v.category(input.cityCode() + "|open")));
            return SearchRequest.of(s -> s.index(INDEX).size(0).suggest(g -> g.suggesters("places",
                    f -> f.prefix(q).completion(c -> c.field("suggest").size(10).skipDuplicates(false)
                            .contexts("scope", List.of(scope))))));
        }
        Query lexical = switch (input.mode()) {
            case "sayt" -> Query.of(qb -> qb.multiMatch(m -> m.query(q).type(TextQueryType.BoolPrefix)
                    .fields("name_sayt", "name_sayt._2gram", "name_sayt._3gram").operator(Operator.And)));
            case "pinyin" -> Query.of(qb -> qb.bool(b -> b
                    .should(v -> v.prefix(p -> p.field("pinyin_full").value(q)))
                    .should(v -> v.prefix(p -> p.field("pinyin_initials").value(q))).minimumShouldMatch("1")));
            case "exact" -> Query.of(qb -> qb.term(t -> t.field("name.whole").value(q)));
            case "guarded" -> q.codePointCount(0, q.length()) < 4
                    ? Query.of(qb -> qb.term(t -> t.field("name.whole").value(q))) : fuzzy(q, 1);
            case "fuzzy" -> fuzzy(q, 0);
            default -> throw new IllegalArgumentException("Unknown suggestion mode");
        };
        return SearchRequest.of(s -> s.index(INDEX).size(20).trackTotalHits(t -> t.enabled(true)).trackScores(true)
                .query(v -> v.bool(b -> b.must(lexical)
                        .filter(f -> f.term(t -> t.field("city_code").value(input.cityCode())))
                        .filter(f -> f.term(t -> t.field("status").value("open")))
                        .filter(f -> f.term(t -> t.field("currency").value("CNY")))))
                .sort(v -> v.field(f -> f.field("attraction_id").order(SortOrder.Asc))));
    }

    private Query fuzzy(String q, int prefixLength) {
        return Query.of(v -> v.fuzzy(f -> f.field("name.whole").value(q).fuzziness("1")
                .prefixLength(prefixLength).maxExpansions(20).transpositions(true).rewrite("constant_score_blended")));
    }

    private Card card(SuggestInput input, String id, SuggestAttraction source, Double score,
                      String text, List<Object> sort) {
        // Reject inconsistent context/source data instead of filtering after a limited top-N lookup.
        if (source == null || id == null || !id.equals(source.attractionId()) || source.name() == null
                || source.pinyinFull() == null || source.pinyinInitials() == null || source.ticketPriceFen() == null
                || source.ticketPriceFen() < 0 || !input.cityCode().equals(source.cityCode())
                || !"open".equals(source.status()) || !"CNY".equals(source.currency()) || score == null)
            throw new AttractionSearchService.IncompleteSearchException();
        return new Card(id, source.name(), source.pinyinFull(), source.pinyinInitials(), source.cityCode(),
                source.ticketPriceFen(), source.currency(), source.status(), score, text, sort);
    }

    public Result search(SuggestInput input) throws IOException {
        var request = request(input);
        var response = client.search(request, SuggestAttraction.class);
        if (response.timedOut() || response.shards().failed().longValue() != 0)
            throw new AttractionSearchService.IncompleteSearchException();
        List<Card> raw = new ArrayList<>();
        Long total = null;
        String relation = "not_available";
        boolean completion = input.mode().equals("completion");
        if (completion) {
            var entries = response.suggest().get("places");
            if (entries == null || entries.size() != 1 || !entries.getFirst().isCompletion())
                throw new AttractionSearchService.IncompleteSearchException();
            for (var option : entries.getFirst().completion().options()) {
                if (option.text() == null) throw new AttractionSearchService.IncompleteSearchException();
                raw.add(card(input, option.id(), option.source(), option.score(), option.text(), List.of()));
            }
        } else {
            if (response.hits().total() == null) throw new AttractionSearchService.IncompleteSearchException();
            total = response.hits().total().value(); relation = response.hits().total().relation().jsonValue();
            for (var hit : response.hits().hits()) {
                List<Object> sort = hit.sort().stream().map(v -> (Object) v._get()).toList();
                raw.add(card(input, hit.id(), hit.source(), hit.score(), null, sort));
            }
        }
        var byId = new LinkedHashMap<String, Card>();
        for (Card item : raw) byId.putIfAbsent(item.id(), item);
        var items = List.copyOf(byId.values());
        return new Result(input, normalized(input), completion ? 10 : 20, raw.size(), items.size(), total,
                relation, response.took(), "business-id", json.readTree(JsonpUtils.toJsonString(request, client._jsonpMapper())),
                json.readTree(JsonpUtils.toJsonString(response, client._jsonpMapper())), items);
    }
}
