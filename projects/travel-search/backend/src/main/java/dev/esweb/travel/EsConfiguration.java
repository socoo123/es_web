package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.json.jackson.Jackson3JsonpMapper;
import java.io.InputStream;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.KeyStore;
import java.security.cert.CertificateFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class EsConfiguration {
    @Bean(destroyMethod = "close")
    ElasticsearchClient elasticsearchClient(@Value("${travel.es-url}") String url,
            @Value("${travel.es-ca-file:}") String caFile,
            @Value("${travel.es-api-key-file:}") String apiKeyFile) throws Exception {
        return connect(url, caFile, apiKeyFile);
    }

    public static ElasticsearchClient connect(String url, String caFile, String apiKeyFile) throws Exception {
        URI endpoint = URI.create(url);
        if (endpoint.getHost() == null || endpoint.getUserInfo() != null
                || endpoint.getQuery() != null || endpoint.getFragment() != null
                || !("http".equals(endpoint.getScheme()) || "https".equals(endpoint.getScheme()))) {
            throw new IllegalArgumentException("ES endpoint must be an HTTP(S) URL without credentials, query or fragment");
        }
        if (caFile.isBlank() && apiKeyFile.isBlank()) {
            return ElasticsearchClient.of(builder -> builder.host(endpoint)
                    .jsonMapper(new Jackson3JsonpMapper()));
        }
        if (!"https".equals(endpoint.getScheme()) || caFile.isBlank() || apiKeyFile.isBlank()) {
            throw new IllegalArgumentException("Secure ES configuration requires HTTPS, a CA file and an API key file");
        }
        String apiKey = Files.readString(Path.of(apiKeyFile), StandardCharsets.UTF_8).strip();
        if (!apiKey.matches("[A-Za-z0-9+/]+={0,2}")) {
            throw new IllegalArgumentException("ES API key file must contain the encoded key only");
        }
        KeyStore trustStore = KeyStore.getInstance("PKCS12");
        trustStore.load(null, null);
        try (InputStream input = Files.newInputStream(Path.of(caFile))) {
            trustStore.setCertificateEntry("f35-ca", CertificateFactory.getInstance("X.509")
                    .generateCertificate(input));
        }
        TrustManagerFactory trust = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        trust.init(trustStore);
        SSLContext tls = SSLContext.getInstance("TLS");
        tls.init(null, trust.getTrustManagers(), null);
        return ElasticsearchClient.of(builder -> builder.host(endpoint).sslContext(tls).apiKey(apiKey)
                .jsonMapper(new Jackson3JsonpMapper()));
    }
}
