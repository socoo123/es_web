FROM docker.elastic.co/elasticsearch/elasticsearch:9.4.0
COPY --chown=elasticsearch:root .artifacts/analysis-icu.zip /tmp/f16-icu.zip
RUN bin/elasticsearch-plugin install --batch file:///tmp/f16-icu.zip \
 && rm /tmp/f16-icu.zip
