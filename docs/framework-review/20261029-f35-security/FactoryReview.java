import dev.esweb.travel.EsConfiguration;

/** Author checks of configuration rejection before any request or credential transmission. */
public class FactoryReview {
    static int rejected;
    static void reject(String url, String ca, String key) throws Exception {
        try (var ignored = EsConfiguration.connect(url, ca, key)) {
            throw new AssertionError("Invalid secure configuration accepted");
        } catch (IllegalArgumentException expected) {
            rejected++;
        }
    }
    public static void main(String[] args) throws Exception {
        reject("http://127.0.0.1:19935", args[0], args[1]);
        reject("https://127.0.0.1:19935", "", args[1]);
        reject("https://127.0.0.1:19935", args[0], "");
        reject("https://example:placeholder@127.0.0.1:19935", args[0], args[1]);
        reject("https://127.0.0.1:19935/?key=placeholder", args[0], args[1]);
        reject("https://127.0.0.1:19935/#placeholder", args[0], args[1]);
        try (var legacy = EsConfiguration.connect("http://127.0.0.1:19200", "", "")) {
            if (legacy == null) throw new AssertionError("Legacy factory");
        }
        System.out.println("{\"rejected_insecure_or_partial_configurations\":" + rejected
                + ",\"legacy_client_constructed_and_closed\":true,\"legacy_es_request_executed\":false,\"passed\":true}");
    }
}
