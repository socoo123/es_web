package dev.esweb.travel;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.json.jackson.Jackson3JsonpMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class EsConfiguration {
    @Bean(destroyMethod = "close")
    ElasticsearchClient elasticsearchClient(@Value("${travel.es-url}") String url) {
        return ElasticsearchClient.of(builder -> builder
                .host(url)
                .jsonMapper(new Jackson3JsonpMapper()));
    }
}
