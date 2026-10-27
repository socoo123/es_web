package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOptions;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.BoolQuery;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.JsonData;
import co.elastic.clients.json.JsonpSerializable;
import co.elastic.clients.json.JsonpUtils;
import java.io.IOException;
import java.time.LocalDate;
import java.util.*;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class CollapseSearchService {
    private static final String SNAPSHOT = "f26-20261027-v1";
    private final ElasticsearchClient client;
    private final JsonMapper json;
    private final Map<String, JsonNode> table = new LinkedHashMap<>();
    public CollapseSearchService(ElasticsearchClient client, JsonMapper json) throws IOException {
        this.client=client; this.json=json;
        try (var stream=new ClassPathResource("f26/stay-table.json").getInputStream()) {
            JsonNode root=json.readTree(stream);
            require(root.path("snapshot_id").asString().equals(SNAPSHOT));
            for (JsonNode offer:root.get("offers")) {
                JsonNode s=offer.get("summary"); String id=s.get("offer_id").asString();
                require(s.get("snapshot_id").asString().equals(SNAPSHOT) && table.putIfAbsent(id,offer)==null);
                Set<String> dates=new HashSet<>();
                for (JsonNode n:offer.get("nights")) {
                    require(dates.add(LocalDate.parse(n.get("date").asString()).toString()));
                    require(n.get("available_rooms").isIntegralNumber() && n.get("available_rooms").asInt()>=0);
                    require(n.get("min_stay_arrival").isIntegralNumber() && n.get("min_stay_arrival").asInt()>=1);
                    require(!n.hasNonNull("price_minor") || (n.get("price_minor").isIntegralNumber() && n.get("price_minor").asLong()>=0));
                }
            }
        }
    }
    public record Decision(String offerId, String hotelId, String hotelName, String reason,
            Long totalMinor, JsonNode nights) {}
    public record Hotel(String hotelId, String hotelName, String minimumOfferId, long minimumTotalMinor,
            List<String> acceptedOfferIds) {}
    public record Result(CollapseInput conditions, String snapshotId, String boundary, boolean completeCandidateSet,
            long candidateOfferTotal, double candidateHotelEstimate, int inspectedOfferCount, int inspectedHotelCount,
            int acceptedOfferCount, int displayedHotelCount, List<Hotel> hotels, List<Decision> decisions,
            JsonNode esRequest, JsonNode esResponse) {}
    private static void require(boolean ok) { if (!ok) throw new AttractionSearchService.IncompleteSearchException(); }
    private JsonNode tree(JsonpSerializable v) { return json.readTree(JsonpUtils.toJsonString(v,client._jsonpMapper())); }
    public SearchRequest request(CollapseInput input) {
        var b=new BoolQuery.Builder();
        for (String[] p:new String[][]{{"city_code","HZ"},{"hotel_status","open"},{"offer_status","active"},
                {"bed_type","twin"},{"meal","breakfast"},{"cancellation","flexible"},{"currency","CNY"}})
            b.filter(q->q.term(t->t.field(p[0]).value(p[1])));
        b.filter(q->q.range(r->r.number(n->n.field("capacity").gte(2.0))));
        b.filter(q->q.range(r->r.date(d->d.field("window_start").lte("2026-11-01"))));
        b.filter(q->q.range(r->r.date(d->d.field("window_end_exclusive").gte("2026-11-03"))));
        b.filter(q->q.range(r->r.number(n->n.field("max_available_rooms").gte(1.0))));
        b.filter(q->q.exists(e->e.field("min_price_minor")));
        List<SortOptions> sort=new ArrayList<>();
        for (String field:List.of("min_price_minor","hotel_id","offer_id"))
            sort.add(SortOptions.of(s->s.field(f->f.field(field).order(SortOrder.Asc))));
        var r=new SearchRequest.Builder().index("tut-f26-offers").size(input.mode().equals("all")?100:2)
                .trackTotalHits(t->t.enabled(true)).query(q->q.bool(b.build())).sort(sort)
                .aggregations("candidate_hotels",a->a.cardinality(c->c.field("hotel_id").precisionThreshold(100)));
        if (input.mode().equals("top-hotels"))
            r.collapse(c->c.field("hotel_id").innerHits(i->i.name("offers").size(10).sort(sort)));
        return r.build();
    }
    private JsonNode source(String id, JsonNode s) {
        require(s!=null && s.hasNonNull("offer_id") && id.equals(s.get("offer_id").asString()));
        JsonNode offer=table.get(id);
        require(offer!=null && offer.get("summary").equals(s)); // fail closed on missing/stale/altered identity or summary
        return s;
    }
    private Decision decide(JsonNode s) {
        String id=s.get("offer_id").asString(); JsonNode nights=table.get(id).get("nights");
        Map<String,JsonNode> byDate=new HashMap<>();
        for (JsonNode n:nights) byDate.put(n.get("date").asString(),n);
        String reason="ACCEPTED"; long sum=0;
        JsonNode arrival=byDate.get("2026-11-01");
        if (arrival!=null && arrival.get("min_stay_arrival").asInt()>2) reason="MIN_STAY";
        else for (LocalDate d=LocalDate.of(2026,11,1);d.isBefore(LocalDate.of(2026,11,3));d=d.plusDays(1)) {
            JsonNode n=byDate.get(d.toString());
            if (n==null) reason="MISSING_NIGHT";
            else if (n.get("available_rooms").asInt()<1) reason="SOLD_OUT";
            else if (!n.hasNonNull("price_minor")) reason="MISSING_PRICE";
            if (!reason.equals("ACCEPTED")) break;
            sum=Math.addExact(sum,n.get("price_minor").asLong());
        }
        return new Decision(id,s.get("hotel_id").asString(),s.get("hotel_name").asString(),reason,
                reason.equals("ACCEPTED")?sum:null,nights);
    }
    public Result inspect(CollapseInput input) throws IOException {
        var request=request(input); var response=client.search(request,JsonData.class);
        require(!response.timedOut() && response.shards().failed().longValue()==0 && response.hits().total()!=null
                && response.hits().total().relation().jsonValue().equals("eq"));
        boolean all=input.mode().equals("all"); long total=response.hits().total().value();
        if (all) require(total==response.hits().hits().size()); // fixed full collection limited to 100, never silently truncate
        JsonNode raw=tree(response); Map<String,JsonNode> selected=new LinkedHashMap<>(); Set<String> groups=new HashSet<>();
        for (JsonNode hit:raw.path("hits").path("hits")) {
            JsonNode root=source(hit.path("_id").asString(),hit.get("_source"));
            if (input.mode().equals("top-hotels")) {
                String hotel=root.get("hotel_id").asString(); require(groups.add(hotel));
                JsonNode inner=hit.path("inner_hits").path("offers").path("hits");
                require(inner.path("total").path("relation").asString().equals("eq")
                        && inner.path("total").path("value").asLong()==inner.path("hits").size());
                boolean foundRoot=false;
                for (JsonNode h:inner.path("hits")) {
                    String id=h.path("_id").asString(); JsonNode s=source(id,h.get("_source"));
                    require(s.get("hotel_id").asString().equals(hotel) && selected.putIfAbsent(id,s)==null);
                    foundRoot |= id.equals(root.get("offer_id").asString());
                }
                require(foundRoot); // group representative must also occur in the complete inner collection
            } else require(selected.putIfAbsent(hit.path("_id").asString(),root)==null);
        }
        List<Decision> decisions=selected.values().stream().map(this::decide).toList();
        Map<String,List<Decision>> accepted=new TreeMap<>();
        for (Decision d:decisions) if (d.reason().equals("ACCEPTED"))
            accepted.computeIfAbsent(d.hotelId(),k->new ArrayList<>()).add(d);
        List<Hotel> hotels=new ArrayList<>();
        for (var entry:accepted.entrySet()) {
            var offers=entry.getValue(); offers.sort(Comparator.comparingLong((Decision d)->d.totalMinor()).thenComparing(Decision::offerId));
            Decision best=offers.getFirst();
            hotels.add(new Hotel(best.hotelId(),best.hotelName(),best.offerId(),best.totalMinor(),offers.stream().map(Decision::offerId).toList()));
        }
        hotels.sort(Comparator.comparingLong(Hotel::minimumTotalMinor).thenComparing(Hotel::hotelId));
        String boundary=switch(input.mode()) {
            case "all" -> "本固定快照全部ES候选逐晚核对；合格酒店最低总价全量排序，限100条且完整性检查通过。";
            case "top-hotels" -> "仅前2家候选酒店；每家至多10条并检查完整，能得出这些酒店的最低总价，不能保证全局最低或全局次序。";
            default -> "仅前2条报价；酒店内和酒店间都可能遗漏，只是已检查报价中的最低总价。";
        };
        require(response.aggregations()!=null && response.aggregations().containsKey("candidate_hotels"));
        return new Result(input,SNAPSHOT,boundary,all,total,response.aggregations().get("candidate_hotels").cardinality().value(),
                decisions.size(),(int)decisions.stream().map(Decision::hotelId).distinct().count(),
                (int)decisions.stream().filter(d->d.reason().equals("ACCEPTED")).count(),hotels.size(),
                List.copyOf(hotels),decisions,tree(request),raw);
    }
}
