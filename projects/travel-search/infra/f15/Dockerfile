FROM docker.elastic.co/elasticsearch/elasticsearch:9.4.0
COPY --chown=elasticsearch:root .artifacts/analysis-ik.zip /tmp/analysis-ik.zip
RUN bin/elasticsearch-plugin install --batch file:///tmp/analysis-ik.zip \
 && rm /tmp/analysis-ik.zip
