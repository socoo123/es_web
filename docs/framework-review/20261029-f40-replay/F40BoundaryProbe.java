import dev.esweb.travel.EsConfiguration;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.apache.kafka.clients.consumer.ConsumerRecord;

/** Author-only synthetic boundary probe. Never commits source consumer offsets. */
public class F40BoundaryProbe {
    public static void main(String[] args) throws Exception {
        var fixture=F40Consumer.JSON.readTree(Files.readString(Path.of(args[0])));
        var r=new ConsumerRecord<String,String>(fixture.path("topic").asString(),0,
            fixture.path("synthetic_offset").asLong(),fixture.path("key").asString(),fixture.path("value").asString());
        boolean shouldBlock=fixture.path("should_block").asBoolean(),blocked=false;
        try(var es=EsConfiguration.connect("http://127.0.0.1:20440","","");var producer=F40Consumer.producer()) {
            try { F40Consumer.apply(es,producer,List.of(r),true); }
            catch(IllegalStateException e) { blocked=true; }
        }
        if(blocked!=shouldBlock) throw new IllegalStateException("Incorrect park classification");
        F40Consumer.log(java.util.Map.of("kind","synthetic_boundary_result","blocked",blocked,
            "source_offsets_changed",false,"passed",true));
    }
}
