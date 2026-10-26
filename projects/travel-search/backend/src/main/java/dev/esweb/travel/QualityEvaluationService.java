package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.*;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonpSerializable;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class QualityEvaluationService {
    private static final String INDEX = "tut-f22-attractions";
    private static final int K = 10;
    private final ElasticsearchClient client;
    private final JsonMapper json;
    private final Fixture fixture;

    public record Task(String id, String split, String text, String intent, Map<String, Integer> ratings) {}
    public record Fixture(String version, String index, int k, int relevantThreshold, List<Task> queries) {}
    public record Metrics(double recall, double ndcg, double dcg, double ideal_dcg,
                          long relevant_docs, long relevant_retrieved) {}
    public record Row(String id, String text, String intent, List<String> ids, List<Integer> grades,
                      double recall, double ndcg, double dcg, double ideal_dcg,
                      long relevant_docs, long relevant_retrieved, long total,
                      JsonNode esRequest, JsonNode esResponse) {}
    public record Result(QualityInput conditions, String fixtureVersion, int k, int relevantThreshold,
                         Map<String, Double> macro, List<Row> queries) {}

    public QualityEvaluationService(ElasticsearchClient client, JsonMapper json) throws IOException {
        this.client = client;
        this.json = json;
        try (var stream = new ClassPathResource("f22/evaluation.json").getInputStream()) {
            fixture = json.readValue(stream, Fixture.class);
        }
        if (!INDEX.equals(fixture.index()) || fixture.k() != K || fixture.relevantThreshold() != 2
                || fixture.queries().size() != 8 || fixture.queries().stream().anyMatch(q ->
                q.ratings().size() != 24 || q.ratings().values().stream().anyMatch(g -> g == null || g < 0 || g > 3)))
            throw new IllegalStateException("Invalid F22 fixed judgment fixture");
    }

    public SearchRequest request(Task task, String strategy) {
        var bool = new BoolQuery.Builder()
                .must(q -> q.multiMatch(m -> m.query(task.text()).fields("name", "description")
                        .type(TextQueryType.BestFields).operator(Operator.Or)))
                .filter(q -> q.term(t -> t.field("city_code").value("HZ")))
                .filter(q -> q.term(t -> t.field("status").value("open")))
                .filter(q -> q.term(t -> t.field("currency").value("CNY")))
                .filter(q -> q.range(r -> r.number(n -> n.field("ticket_price_fen").gte(0.0).lte(10000.0))))
                .minimumShouldMatch("0");
        if (strategy.equals("candidate")) {
            bool.should(q -> q.match(m -> m.field("name").query(task.text()).operator(Operator.And).boost(2.0f)));
            bool.should(q -> q.matchPhrase(m -> m.field("name").query(task.text()).boost(4.0f)));
        }
        return new SearchRequest.Builder().index(INDEX).size(K).trackTotalHits(t -> t.enabled(true))
                .query(q -> q.bool(bool.build()))
                .sort(s -> s.score(v -> v.order(SortOrder.Desc)))
                .sort(s -> s.field(f -> f.field("attraction_id").order(SortOrder.Asc))).build();
    }

    private double dcg(List<Integer> grades) {
        double value = 0;
        for (int i = 0; i < grades.size(); i++)
            value += (Math.pow(2, grades.get(i)) - 1) / (Math.log(i + 2) / Math.log(2));
        return value;
    }

    public Metrics metrics(List<Integer> grades, Map<String, Integer> ratings) {
        long relevant = ratings.values().stream().filter(g -> g >= 2).count();
        long retrieved = grades.stream().filter(g -> g >= 2).count();
        // Standard IDCG@10 uses all judged documents, independent of the returned length.
        double ideal = dcg(ratings.values().stream().sorted(Comparator.reverseOrder()).limit(K).toList());
        double actual = dcg(grades);
        return new Metrics(relevant == 0 ? 0 : (double) retrieved / relevant,
                ideal == 0 ? 0 : actual / ideal, actual, ideal, relevant, retrieved);
    }

    private JsonNode tree(JsonpSerializable value) {
        return json.readTree(JsonpUtils.toJsonString(value, client._jsonpMapper()));
    }

    public Result evaluate(QualityInput input) throws IOException {
        var tasks = fixture.queries().stream().filter(q -> q.split().equals(input.split())).toList();
        var rows = new ArrayList<Row>();
        for (var task : tasks) {
            var request = request(task, input.strategy());
            var response = client.search(request, QualityAttraction.class);
            if (response.timedOut() || response.shards().failed().longValue() != 0
                    || response.hits().total() == null
                    || !response.hits().total().relation().jsonValue().equals("eq"))
                throw new AttractionSearchService.IncompleteSearchException();
            var ids = new ArrayList<String>();
            var grades = new ArrayList<Integer>();
            for (var hit : response.hits().hits()) {
                var source = hit.source();
                if (source == null || !hit.id().equals(source.attractionId()) || source.name() == null
                        || source.description() == null || !"HZ".equals(source.cityCode())
                        || !"open".equals(source.status()) || !"CNY".equals(source.currency())
                        || source.ticketPriceFen() == null || source.ticketPriceFen() < 0
                        || source.ticketPriceFen() > 10000 || hit.score() == null || hit.sort().size() != 2
                        || !task.ratings().containsKey(hit.id()))
                    throw new AttractionSearchService.IncompleteSearchException();
                ids.add(hit.id());
                grades.add(task.ratings().get(hit.id()));
            }
            if (new HashSet<>(ids).size() != ids.size())
                throw new AttractionSearchService.IncompleteSearchException();
            var metric = metrics(grades, task.ratings());
            rows.add(new Row(task.id(), task.text(), task.intent(), ids, grades,
                    metric.recall(), metric.ndcg(), metric.dcg(), metric.ideal_dcg(),
                    metric.relevant_docs(), metric.relevant_retrieved(), response.hits().total().value(),
                    tree(request), tree(response)));
        }
        if (rows.isEmpty()) throw new AttractionSearchService.IncompleteSearchException();
        return new Result(input, fixture.version(), K, 2,
                Map.of("recall", rows.stream().mapToDouble(Row::recall).average().orElseThrow(),
                       "ndcg", rows.stream().mapToDouble(Row::ndcg).average().orElseThrow()), rows);
    }
}
