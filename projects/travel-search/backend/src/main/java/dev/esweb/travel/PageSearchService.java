package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.*;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.core.search.TotalHitsRelation;
import co.elastic.clients.json.JsonpUtils;
import jakarta.annotation.PreDestroy;
import java.io.IOException;
import java.time.Instant;
import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

@Service
@EnableScheduling
public class PageSearchService {
    static final class Session {
        final PageInput input;
        String pit;
        List<FieldValue> after = List.of();
        int page;
        long seen, total;
        Instant expires;
        Session(PageInput input, String pit) { this.input = input; this.pit = pit; }
    }
    public static final class PageFault extends RuntimeException {
        final int status;
        final String code;
        PageFault(int status, String code, String message) { super(message); this.status = status; this.code = code; }
    }
    private final ElasticsearchClient client;
    private final SortSearchService sorts;
    private final JsonMapper json;
    private final String index;
    private final Map<String, Session> sessions = new HashMap<>();

    public PageSearchService(ElasticsearchClient client, SortSearchService sorts, JsonMapper json,
            @Value("${travel.f11-index:tut-f11-attractions}") String index) {
        this.client = client; this.sorts = sorts; this.json = json; this.index = index;
    }
    SearchRequest request(Session s) {
        var base = sorts.request(s.input.search());
        var builder = new SearchRequest.Builder().size(s.input.pageSize())
                .query(base.query()).source(base.source()).sort(base.sort())
                .sort(v -> v.field(f -> f.field("_shard_doc").order(SortOrder.Asc)))
                .trackScores(s.input.search().trackScores()).trackTotalHits(t -> t.enabled(true))
                .allowPartialSearchResults(false).pit(p -> p.id(s.pit).keepAlive(t -> t.time("1m")));
        if (!s.after.isEmpty()) builder.searchAfter(s.after);
        return builder.build(); // PIT carries the index; do not set index/routing/preference here.
    }
    private void release(Session s) throws IOException {
        client.closePointInTime(c -> c.id(s.pit));
    }
    private void discard(String cursor, Session s) {
        sessions.remove(cursor);
        try { release(s); } catch (Exception ignored) { /* ES keep_alive is the fallback. */ }
    }
    public synchronized PageResult start(PageInput input) throws IOException {
        reap();
        if (sessions.size() >= 100) throw new PageFault(429, "PAGE_LIMIT", "本机分页会话过多，请关闭旧会话后重试。");
        var opened = client.openPointInTime(o -> o.index(index).keepAlive(t -> t.time("1m"))
                .allowPartialSearchResults(false));
        var s = new Session(input, opened.id());
        String cursor = UUID.randomUUID().toString();
        try {
            var result = read(cursor, s);
            sessions.put(cursor, s);
            return result;
        } catch (IOException | RuntimeException error) { discard(cursor, s); throw error; }
    }
    public synchronized PageResult next(PageController.Turn turn) throws IOException {
        var s = sessions.get(turn.cursor());
        if (s == null) throw new PageFault(410, "PAGE_EXPIRED", "分页已关闭、过期或服务已重启，请从第一页开始。");
        if (!Instant.now().isBefore(s.expires)) {
            discard(turn.cursor(), s);
            throw new PageFault(410, "PAGE_EXPIRED", "分页已过期，请从第一页开始。");
        }
        if (!s.input.equals(turn.conditions()) || s.page != turn.afterPage())
            throw new PageFault(409, "PAGE_CHANGED", "条件或页序已改变，请关闭旧分页并重新搜索。");
        if (s.seen >= s.total) throw new PageFault(409, "PAGE_END", "已到末页，请关闭分页或重新搜索。");
        try { return read(turn.cursor(), s); }
        catch (ElasticsearchException error) {
            discard(turn.cursor(), s);
            if (error.status() == 404) throw new PageFault(410, "PAGE_EXPIRED", "ES 搜索视图已失效，请从第一页开始。");
            throw error;
        } catch (IOException | RuntimeException error) {
            discard(turn.cursor(), s); // A failed turn must not be silently advanced/retried.
            throw error;
        }
    }
    private PageResult read(String cursor, Session s) throws IOException {
        var request = request(s);
        var response = client.search(request, SortAttraction.class);
        if (response.pitId() != null) s.pit = response.pitId(); // Keep the latest ID even before validation.
        var total = response.hits().total();
        if (response.timedOut() || response.shards().failed().longValue() != 0 || total == null
                || total.relation() != TotalHitsRelation.Eq || (s.page > 0 && total.value() != s.total))
            throw new AttractionSearchService.IncompleteSearchException();
        var hits = response.hits().hits();
        var cards = hits.stream().map(hit -> {
            var src = hit.source();
            if (src == null || !hit.id().equals(src.attractionId()) || src.name() == null
                    || src.ticketPriceFen() == null || hit.sort().size() != 3)
                throw new AttractionSearchService.IncompleteSearchException();
            var values = hit.sort().stream().map(v -> (Object) switch (v._kind()) {
                case Long -> v.longValue();
                case Double -> v.doubleValue();
                case String -> v.stringValue();
                default -> throw new AttractionSearchService.IncompleteSearchException();
            }).toList();
            return new PageResult.Card(hit.id(), src.name(), src.ticketPriceFen(), hit.score(), values);
        }).toList();
        long seen = s.seen + cards.size();
        if (seen > total.value() || (cards.isEmpty() && seen < total.value()))
            throw new AttractionSearchService.IncompleteSearchException();
        if (!hits.isEmpty()) s.after = List.copyOf(hits.getLast().sort()); // No rounding/string reconstruction.
        s.seen = seen; s.total = total.value(); s.page++;
        s.expires = Instant.now().plusSeconds(60);
        return new PageResult(cursor, s.page, s.seen < s.total, s.total, total.relation().jsonValue(),
                s.input, json.readTree(JsonpUtils.toJsonString(request, client._jsonpMapper())), cards);
    }
    public synchronized Object close(String cursor) throws IOException {
        var s = sessions.get(cursor);
        if (s == null) return Map.of("closed", true, "alreadyGone", true);
        var response = client.closePointInTime(c -> c.id(s.pit));
        if (!response.succeeded()) throw new AttractionSearchService.IncompleteSearchException();
        sessions.remove(cursor);
        return Map.of("closed", true, "numFreed", response.numFreed());
    }
    @Scheduled(fixedDelay = 5000)
    public synchronized void reap() {
        var now = Instant.now();
        for (var entry : new ArrayList<>(sessions.entrySet()))
            if (!now.isBefore(entry.getValue().expires)) discard(entry.getKey(), entry.getValue());
    }
    @PreDestroy
    public synchronized void shutdown() {
        for (var entry : new ArrayList<>(sessions.entrySet())) discard(entry.getKey(), entry.getValue());
    }
}
