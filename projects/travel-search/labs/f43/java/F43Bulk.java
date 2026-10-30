import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.ElasticsearchException;
import co.elastic.clients.elasticsearch.core.BulkRequest;
import co.elastic.clients.json.JsonData;
import dev.esweb.travel.EsConfiguration;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import tools.jackson.databind.json.JsonMapper;

/** Bounded Bulk experiment, not a background ingestion service. */
public class F43Bulk {
    static final JsonMapper JSON=JsonMapper.builder().build();
    record Doc(String id,JsonData body,int bytes) {}
    record Result(int successes,int failures,int attempts,int rejected,List<Object> trace) {}
    static Result send(ElasticsearchClient es,String index,List<Doc> input,Random jitter) throws Exception {
        var pending=new ArrayList<>(input);
        int ok=0,failed=0,rejected=0,attempts=0;
        var trace=new ArrayList<Object>();
        for(int retry=0;!pending.isEmpty();retry++) {
            var request=new BulkRequest.Builder();
            for(var doc:pending) request.operations(o->o.index(i->i.index(index).id(doc.id()).document(doc.body())));
            var next=new ArrayList<Doc>();var errors=new ArrayList<Object>();
            long start=System.nanoTime();int http=200;attempts++;
            try {
                var reply=es.bulk(request.build());
                if(reply.items().size()!=pending.size())throw new IllegalStateException("Bulk item count mismatch");
                for(int i=0;i<pending.size();i++) {
                    var item=reply.items().get(i);var doc=pending.get(i);
                    if(!doc.id().equals(item.id()))throw new IllegalStateException("Bulk ID mismatch");
                    if(item.status()<300 && item.error()==null) ok++;
                    else {
                        errors.add(Map.of("id",doc.id(),"status",item.status(),"error",String.valueOf(item.error())));
                        if(item.status()==429) {next.add(doc);rejected++;} else failed++;
                    }
                }
            } catch(ElasticsearchException e) {
                http=e.status();errors.add(Map.of("status",http,"error",e.toString()));
                if(http==429) {next.addAll(pending);rejected+=pending.size();} else failed+=pending.size();
            }
            // Transport failures are deliberately not retried: the outcome may be unknown.
            trace.add(Map.of("http",http,"documents",pending.size(),"ms",(System.nanoTime()-start)/1e6,"errors",errors));
            if(next.isEmpty())break;
            if(retry==3) {failed+=next.size();break;}
            int waitMs=jitter.nextInt(50*(1<<retry)+1);
            trace.add(Map.of("backoff_ms",waitMs));Thread.sleep(waitMs);
            pending=next; // Only rejected items, never the already successful ones.
        }
        return new Result(ok,failed,attempts,rejected,trace);
    }
    static double percentile(List<Double> values,double p) {
        if(values.isEmpty())return 0;
        return values.stream().sorted().toList().get((int)Math.ceil(values.size()*p)-1);
    }
    public static void main(String[] args) throws Exception {
        // index corpus batch workers output; all source construction precedes timing.
        if(args.length!=5)throw new IllegalArgumentException("index corpus batch workers output");
        String index=args[0];int batch=Integer.parseInt(args[2]),workers=Integer.parseInt(args[3]);
        if(!index.matches("tut-f43-(import|load|pressure|warmup)"))throw new IllegalArgumentException("F43 index required");
        if(batch<1||batch>500||workers<1||workers>4)throw new IllegalArgumentException("Bounded batch/workers required");
        Path output=Path.of(args[4]);if(Files.exists(output))throw new IllegalArgumentException("New output required");
        var documents=new ArrayList<Doc>();
        for(String line:Files.readAllLines(Path.of(args[1]),StandardCharsets.UTF_8)) {
            var node=JSON.readTree(line);String id=node.path("attraction_id").asString("");
            if(!id.matches("p[0-9]{6}"))throw new IllegalArgumentException("Invalid synthetic ID");
            documents.add(new Doc(id,JsonData.fromJson(line),line.getBytes(StandardCharsets.UTF_8).length));
        }
        var samples=new ConcurrentLinkedQueue<Map<String,Object>>();
        try(var es=EsConfiguration.connect("http://127.0.0.1:20743","","");var pool=Executors.newFixedThreadPool(workers)) {
            // Connection/JIT warmup is explicit and separate from the measured index.
            if(!index.equals("tut-f43-pressure")) {
                var warm=send(es,"tut-f43-warmup",documents.subList(0,Math.min(500,documents.size())),new Random(43));
                if(warm.failures()!=0)throw new IllegalStateException("Warmup failed");
            }
            var tasks=new ArrayList<Callable<Void>>();
            for(int w=0;w<workers;w++) {
                int worker=w;
                tasks.add(()-> {
                    var random=new Random(4300+worker);
                    for(int from=worker*batch;from<documents.size();from+=workers*batch) {
                        var part=documents.subList(from,Math.min(from+batch,documents.size()));
                        long t=System.nanoTime();var result=send(es,index,part,random);
                        var row=new LinkedHashMap<String,Object>();
                        row.put("worker",worker);row.put("first_id",part.getFirst().id());row.put("documents",part.size());
                        row.put("source_bytes",part.stream().mapToInt(Doc::bytes).sum());
                        row.put("ms",(System.nanoTime()-t)/1e6);row.put("successes",result.successes());
                        row.put("failures",result.failures());row.put("attempts",result.attempts());row.put("rejected_attempt_items",result.rejected());
                        row.put("trace",result.trace());samples.add(row);
                    }
                    return null;
                });
            }
            String at=Instant.now().toString();long begin=System.nanoTime();
            for(var future:pool.invokeAll(tasks))future.get();
            double seconds=(System.nanoTime()-begin)/1e9;
            int successes=samples.stream().mapToInt(s->(int)s.get("successes")).sum();
            int failures=samples.stream().mapToInt(s->(int)s.get("failures")).sum();
            var latencies=samples.stream().map(s->(double)s.get("ms")).toList();
            var summary=new LinkedHashMap<String,Object>();
            summary.put("started_at",at);summary.put("index",index);summary.put("documents",documents.size());
            summary.put("batch",batch);summary.put("workers",workers);summary.put("elapsed_seconds",seconds);
            summary.put("successes",successes);summary.put("failures",failures);summary.put("successful_docs_per_second",successes/seconds);
            summary.put("bulk_p50_ms",percentile(latencies,.5));summary.put("bulk_p95_ms",percentile(latencies,.95));
            summary.put("bulk_p99_ms",percentile(latencies,.99));summary.put("samples",samples);
            summary.put("java_runtime",System.getProperty("java.runtime.version"));
            // Exact same REST body is also exercised through the official Java client.
            if(failures==0 && !index.equals("tut-f43-pressure")) {
                es.indices().refresh(r->r.index(index));
                var query=Files.readString(Path.of("search/f43/query.json"));
                var reply=es.search(s->s.index(index).allowPartialSearchResults(false).requestCache(false)
                    .withJson(new java.io.StringReader(query)),JsonData.class);
                if(reply.timedOut()||reply.shards().failed().intValue()!=0||reply.hits().total().value()!=documents.size()/4)
                    throw new IllegalStateException("Java search contract mismatch");
                summary.put("java_search_ids",reply.hits().hits().stream().map(h->h.id()).toList());
                summary.put("java_search_total",reply.hits().total().value());
            }
            Files.writeString(output,JSON.writerWithDefaultPrettyPrinter().writeValueAsString(summary)+"\n");
            System.out.println(JSON.writeValueAsString(Map.of("index",index,"successes",successes,"failures",failures,"seconds",seconds)));
            if(failures!=0)System.exit(2);
        }
    }
}
