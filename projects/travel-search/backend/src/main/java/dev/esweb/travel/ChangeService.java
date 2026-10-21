package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.ElasticsearchException;
import co.elastic.clients.elasticsearch._types.Refresh;
import jakarta.annotation.PreDestroy;
import java.io.IOException;
import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import tools.jackson.databind.json.JsonMapper;

@Service
public class ChangeService {
    public static final class ChangeFault extends RuntimeException {
        final int status; final String code;
        ChangeFault(int status, String code, String message) {
            super(message); this.status = status; this.code = code;
        }
    }
    public record Read(String id, long seqNo, long primaryTerm, ChangeDocument document) { }
    public record Written(String id, String result, long seqNo, long primaryTerm) { }
    private final ElasticsearchClient client;
    private final String index;
    private final PageSearchService pages;

    public ChangeService(ElasticsearchClient client, SortSearchService sorts, JsonMapper json,
            @Value("${travel.f12-index:tut-f12-attractions}") String index) {
        this.client = client; this.index = index;
        this.pages = new PageSearchService(client, sorts, json, index);
    }
    private ChangeFault missing() {
        return new ChangeFault(404, "DOCUMENT_MISSING", "资料不存在，请重新读取并确认是否已被删除。");
    }
    private RuntimeException translate(ElasticsearchException error) {
        if (error.status() == 409)
            return new ChangeFault(409, "WRITE_CONFLICT", "版本已变化或ID已存在；请重新读取、核对他人修改，再决定是否重试。");
        if (error.status() == 404 && error.error().type().equals("document_missing_exception")) return missing();
        return error; // Missing index and other backend errors remain 502 through ApiErrors.
    }
    public Read get(String id) throws IOException {
        var r = client.get(g -> g.index(index).id(id).realtime(true), ChangeDocument.class);
        if (!r.found()) throw missing();
        if (r.source() == null || !id.equals(r.source().attractionId()))
            throw new AttractionSearchService.IncompleteSearchException();
        return new Read(id, r.seqNo(), r.primaryTerm(), r.source());
    }
    private void sameId(String id, ChangeDocument doc) {
        if (!id.equals(doc.attractionId()))
            throw new ChangeFault(400, "DOCUMENT_ID_MISMATCH", "路径ID必须与attraction_id一致。");
    }
    public Written create(String id, ChangeDocument doc) throws IOException {
        sameId(id, doc);
        try {
            var r = client.create(c -> c.index(index).id(id).document(doc).refresh(Refresh.False));
            return new Written(id, r.result().jsonValue(), r.seqNo(), r.primaryTerm());
        } catch (ElasticsearchException error) { throw translate(error); }
    }
    public Written replace(String id, ChangeController.Replace input) throws IOException {
        sameId(id, input.document());
        try {
            var r = client.index(i -> i.index(index).id(id).document(input.document())
                    .ifSeqNo(input.seqNo()).ifPrimaryTerm(input.primaryTerm()).refresh(Refresh.False));
            return new Written(id, r.result().jsonValue(), r.seqNo(), r.primaryTerm());
        } catch (ElasticsearchException error) { throw translate(error); }
    }
    public Written patch(String id, ChangeController.Patch input) throws IOException {
        var doc = new LinkedHashMap<String, Object>();
        if (input.ticketPriceFen() != null) doc.put("ticket_price_fen", input.ticketPriceFen());
        if (input.status() != null) doc.put("status", input.status());
        try {
            var r = client.update(u -> u.index(index).id(id).doc(doc)
                    .ifSeqNo(input.seqNo()).ifPrimaryTerm(input.primaryTerm()).refresh(Refresh.False), ChangeDocument.class);
            return new Written(id, r.result().jsonValue(), r.seqNo(), r.primaryTerm());
        } catch (ElasticsearchException error) { throw translate(error); }
    }
    public Written delete(String id, ChangeController.Version input) throws IOException {
        try {
            var r = client.delete(d -> d.index(index).id(id).ifSeqNo(input.seqNo())
                    .ifPrimaryTerm(input.primaryTerm()).refresh(Refresh.False));
            return new Written(id, r.result().jsonValue(), r.seqNo(), r.primaryTerm());
        } catch (ElasticsearchException error) { throw translate(error); }
    }
    public Object refresh() throws IOException {
        var r = client.indices().refresh(rq -> rq.index(index));
        if (r.shards().failed().longValue() != 0) throw new AttractionSearchService.IncompleteSearchException();
        return Map.of("refreshed", true, "index", index);
    }
    public PageResult start(PageInput input) throws IOException { return pages.start(input); }
    public PageResult next(PageController.Turn input) throws IOException { return pages.next(input); }
    public Object close(String cursor) throws IOException { return pages.close(cursor); }
    @Scheduled(fixedDelay = 5000)
    public void reap() { pages.reap(); }
    @PreDestroy
    public void shutdown() { pages.shutdown(); }
}
