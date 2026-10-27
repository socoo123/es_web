package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.*;
import co.elastic.clients.elasticsearch._types.query_dsl.*;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.json.*;
import java.io.IOException;
import java.time.*;
import java.util.*;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

@Service
public class HotelRankingService {
    private static final String SNAPSHOT="f27-20261027-v1";
    private static final Instant REFERENCE=Instant.parse("2026-10-27T00:00:00Z");
    private final ElasticsearchClient client;
    private final JsonMapper json;
    private final Map<String,JsonNode> hotels=new HashMap<>(), offers=new HashMap<>();
    public HotelRankingService(ElasticsearchClient client, JsonMapper json) throws IOException {
        this.client=client;this.json=json;
        try(var stream=new ClassPathResource("f27/stay-table.json").getInputStream()) {
            JsonNode root=json.readTree(stream);
            require(root.path("snapshot_id").asString().equals(SNAPSHOT)
                    && Instant.parse(root.path("reference_time").asString()).equals(REFERENCE)
                    && root.path("max_inventory_age_seconds").asInt()==300);
            for(JsonNode h:root.path("hotels")) require(hotels.putIfAbsent(h.path("hotel_id").asString(),h)==null);
            for(JsonNode o:root.path("offers")) {
                String id=o.path("summary").path("offer_id").asString();
                require(offers.putIfAbsent(id,o)==null && hotels.containsKey(o.path("hotel_id").asString()));
                Set<String> dates=new HashSet<>();
                for(JsonNode n:o.path("nights")) {
                    require(dates.add(LocalDate.parse(n.path("date").asString()).toString())
                            && n.path("available_rooms").isIntegralNumber() && n.path("available_rooms").asInt()>=0
                            && n.path("min_stay_arrival").isIntegralNumber() && n.path("min_stay_arrival").asInt()>=1
                            && (!n.hasNonNull("price_minor") || (n.get("price_minor").isIntegralNumber() && n.get("price_minor").asLong()>=0)));
                    Instant.parse(n.path("inventory_as_of").asString());
                }
            }
        }
    }
    private static void require(boolean ok) { if(!ok) throw new AttractionSearchService.IncompleteSearchException(); }
    private JsonNode tree(JsonpSerializable v) { return json.readTree(JsonpUtils.toJsonString(v,client._jsonpMapper())); }
    public record Decision(String hotelId,String offerId,String roomId,String ratePlanId,String meal,String cancellation,
            String reason,Long totalMinor,JsonNode nights) {}
    public record Hotel(String hotelId,String hotelName,JsonNode hotelSortValues,Double score,Long qualitySignal,
            long minimumTotalMinor,String selectedOfferId,long selectedTotalMinor,List<Decision> rooms) {}
    public record Result(HotelRankingInput conditions,String snapshotId,String referenceTime,String boundary,
            boolean completeCandidateSet,long candidateHotelTotal,int inspectedHotelCount,int inspectedOfferCount,
            int acceptedOfferCount,List<Hotel> hotels,List<Decision> decisions,JsonNode esRequest,JsonNode esResponse) {}
    public SearchRequest request(HotelRankingInput input) {
        var offer=new BoolQuery.Builder();
        for(String[] pair:new String[][]{{"offer_status","active"},{"bed_type","twin"},{"currency","CNY"}})
            offer.filter(q->q.term(t->t.field("offers."+pair[0]).value(pair[1])));
        if(input.requireBreakfast())offer.filter(q->q.term(t->t.field("offers.meal").value("breakfast")));
        if(input.requireFlexible())offer.filter(q->q.term(t->t.field("offers.cancellation").value("flexible")));
        offer.filter(q->q.range(r->r.number(n->n.field("offers.capacity").gte(2.0))));
        offer.filter(q->q.range(r->r.date(d->d.field("offers.window_start").lte("2026-11-01"))));
        offer.filter(q->q.range(r->r.date(d->d.field("offers.window_end_exclusive").gte("2026-11-03"))));
        offer.filter(q->q.range(r->r.number(n->n.field("offers.max_available_rooms").gte(1.0))));
        var hotel=new BoolQuery.Builder()
                .must(q->q.multiMatch(m->m.query(input.q()).fields("name_search^5","description")
                        .type(TextQueryType.BestFields).operator(Operator.And)))
                .filter(q->q.term(t->t.field("city_code").value("HZ")))
                .filter(q->q.term(t->t.field("hotel_status").value("open")))
                .filter(q->q.nested(n->n.path("offers").scoreMode(ChildScoreMode.None)
                        .query(v->v.bool(offer.build())).innerHits(i->i.name("eligible_offers").size(20)
                                .sort(s->s.field(f->f.field("offers.offer_id").order(SortOrder.Asc))))));
        var r=new SearchRequest.Builder().index("tut-f27-hotels").size(input.scope().equals("all")?100:2)
                .trackTotalHits(t->t.enabled(true)).trackScores(true).query(q->q.bool(hotel.build()));
        switch(input.hotelSort()) {
            case "relevance" -> r.sort(s->s.score(v->v.order(SortOrder.Desc)));
            case "quality" -> r.sort(s->s.field(f->f.field("quality_signal").order(SortOrder.Desc).missing(FieldValue.of("_last"))));
            case "distance" -> r.sort(s->s.geoDistance(g->g.field("location")
                    .location(l->l.latlon(p->p.lat(30.25).lon(120.15))).order(SortOrder.Asc)
                    .unit(DistanceUnit.Meters).distanceType(GeoDistanceType.Arc).mode(SortMode.Min).ignoreUnmapped(false)));
            default -> throw new IllegalArgumentException("Unsupported hotel sort");
        }
        return r.sort(s->s.field(f->f.field("hotel_id").order(SortOrder.Asc))).build();
    }
    private Decision decide(String hotel,JsonNode s) {
        String id=s.path("offer_id").asString();JsonNode row=offers.get(id);
        require(row!=null && row.path("hotel_id").asString().equals(hotel) && row.path("summary").equals(s));
        JsonNode nights=row.path("nights");Map<String,JsonNode> dates=new HashMap<>();
        for(JsonNode n:nights)dates.put(n.path("date").asString(),n);
        String reason="ACCEPTED";long total=0;
        JsonNode arrival=dates.get("2026-11-01");
        if(arrival!=null && arrival.path("min_stay_arrival").asInt()>2)reason="MIN_STAY";
        else for(LocalDate day=LocalDate.of(2026,11,1);day.isBefore(LocalDate.of(2026,11,3));day=day.plusDays(1)) {
            JsonNode n=dates.get(day.toString());
            if(n==null)reason="MISSING_NIGHT";
            else {
                Duration age=Duration.between(Instant.parse(n.path("inventory_as_of").asString()),REFERENCE);
                if(age.isNegative())reason="FUTURE_INVENTORY";
                else if(age.compareTo(Duration.ofSeconds(300))>0)reason="STALE_INVENTORY";
                else if(n.path("available_rooms").asInt()<1)reason="SOLD_OUT";
                else if(!n.hasNonNull("price_minor"))reason="MISSING_PRICE";
            }
            if(!reason.equals("ACCEPTED"))break;
            total=Math.addExact(total,n.path("price_minor").asLong());
        }
        return new Decision(hotel,id,s.path("room_id").asString(),s.path("rate_plan_id").asString(),
                s.path("meal").asString(),s.path("cancellation").asString(),reason,reason.equals("ACCEPTED")?total:null,nights);
    }
    private Comparator<Decision> roomOrder(HotelRankingInput input) {
        Comparator<Decision> total=Comparator.comparingLong((Decision d)->d.totalMinor())
                .thenComparing(Decision::roomId).thenComparing(Decision::ratePlanId).thenComparing(Decision::offerId);
        if(input.roomSort().equals("total"))return total;
        return Comparator.comparingInt((Decision d)->d.meal().equals("breakfast")?0:1)
                .thenComparingInt(d->d.cancellation().equals("flexible")?0:1).thenComparing(total);
    }
    public Result inspect(HotelRankingInput input) throws IOException {
        var request=request(input);var response=client.search(request,JsonData.class);
        require(!response.timedOut() && response.shards().failed().longValue()==0 && response.hits().total()!=null
                && response.hits().total().relation().jsonValue().equals("eq"));
        boolean complete=input.scope().equals("all");
        if(complete)require(response.hits().total().value()==response.hits().hits().size());
        JsonNode raw=tree(response);List<Hotel> result=new ArrayList<>();List<Decision> decisions=new ArrayList<>();
        Set<String> seenHotels=new HashSet<>(),seenOffers=new HashSet<>();
        for(JsonNode hit:raw.path("hits").path("hits")) {
            String id=hit.path("_id").asString();JsonNode source=hit.get("_source");
            require(seenHotels.add(id) && source!=null && source.equals(hotels.get(id)));
            JsonNode inner=hit.path("inner_hits").path("eligible_offers").path("hits");
            require(inner.path("total").path("relation").asString().equals("eq")
                    && inner.path("total").path("value").asInt()==inner.path("hits").size()
                    && inner.path("hits").size()>0);
            List<Decision> accepted=new ArrayList<>();
            for(JsonNode ih:inner.path("hits")) {
                JsonNode s=ih.get("_source");
                require(s!=null && seenOffers.add(s.path("offer_id").asString()));
                Decision d=decide(id,s);decisions.add(d);
                if(d.reason().equals("ACCEPTED"))accepted.add(d);
            }
            if(accepted.isEmpty())continue; // remove ineligible hotels; preserve ES hotel order
            long minimum=accepted.stream().mapToLong(d->d.totalMinor()).min().orElseThrow();
            accepted.sort(roomOrder(input));Decision selected=accepted.getFirst();
            result.add(new Hotel(id,source.path("hotel_name").asString(),hit.get("sort"),
                    hit.hasNonNull("_score")?hit.get("_score").asDouble():null,
                    source.hasNonNull("quality_signal")?source.get("quality_signal").asLong():null,
                    minimum,selected.offerId(),selected.totalMinor(),List.copyOf(accepted)));
        }
        String boundary=complete
                ?"本固定快照全部ES候选酒店及各酒店匹配报价已完整核对；保持酒店排序，房型只在各酒店内部排序。"
                :"仅ES排序前2家候选酒店；移除不合格酒店后不补位，不能声称完整或全局前2家。";
        return new Result(input,SNAPSHOT,REFERENCE.toString(),boundary,complete,response.hits().total().value(),
                seenHotels.size(),decisions.size(),(int)decisions.stream().filter(d->d.reason().equals("ACCEPTED")).count(),
                List.copyOf(result),List.copyOf(decisions),tree(request),raw);
    }
}
