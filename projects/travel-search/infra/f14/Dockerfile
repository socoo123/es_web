FROM docker.elastic.co/elasticsearch/elasticsearch:9.4.0
COPY --chown=elasticsearch:root .artifacts/*.zip /tmp/f14-plugins/
RUN bin/elasticsearch-plugin install --batch file:///tmp/f14-plugins/analysis-smartcn.zip \
 && bin/elasticsearch-plugin install --batch file:///tmp/f14-plugins/analysis-icu.zip \
 && bin/elasticsearch-plugin install --batch file:///tmp/f14-plugins/analysis-ik.zip \
 && rm -rf /tmp/f14-plugins
