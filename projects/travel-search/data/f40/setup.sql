-- The lab binds cdc_password through psql stdin. Only synthetic lesson data.
CREATE SCHEMA f40;
CREATE TABLE f40.city (city_code text PRIMARY KEY, city_name text NOT NULL);
CREATE TABLE f40.attraction (
  attraction_id text PRIMARY KEY CHECK (attraction_id ~ '^p[0-9]{2}$'),
  name text NOT NULL, city_code text NOT NULL REFERENCES f40.city,
  ticket_price_fen bigint NOT NULL CHECK (ticket_price_fen >= 0),
  status text NOT NULL CHECK (status IN ('open','closed')),
  latitude double precision NOT NULL, longitude double precision NOT NULL
);
CREATE TABLE f40.attraction_tag (
  tag_id text PRIMARY KEY, attraction_id text NOT NULL REFERENCES f40.attraction ON DELETE CASCADE,
  tag text NOT NULL, UNIQUE(attraction_id,tag)
);
-- This row survives physical deletion/recreation of the business root.
CREATE TABLE f40.projection_clock (attraction_id text PRIMARY KEY, revision bigint NOT NULL CHECK (revision > 0));
CREATE TABLE f40.root_event (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  attraction_id text NOT NULL, revision bigint NOT NULL CHECK (revision > 0),
  deleted boolean NOT NULL, document jsonb NOT NULL
);
CREATE TABLE f40.related_event (LIKE f40.root_event INCLUDING ALL);
CREATE FUNCTION f40.project(p_id text) RETURNS jsonb LANGUAGE sql STABLE AS $$
  SELECT jsonb_build_object(
    'attraction_id',a.attraction_id,'name',a.name,'city_code',a.city_code,'city_name',c.city_name,
    'ticket_price_fen',a.ticket_price_fen,'currency','CNY','status',a.status,
    'location',jsonb_build_object('lat',a.latitude,'lon',a.longitude),
    'tags',COALESCE((SELECT jsonb_agg(t.tag ORDER BY t.tag COLLATE "C")
                    FROM f40.attraction_tag t WHERE t.attraction_id=a.attraction_id),'[]'::jsonb))
  FROM f40.attraction a JOIN f40.city c USING(city_code)
  WHERE a.attraction_id=p_id AND a.status='open'
$$;
-- All writers must acquire advisory lock 40040 BEFORE changing business rows,
-- and publish every affected root in that SAME transaction. This is a teaching
-- single-writer contract, not transparent CDC of arbitrary unmodified writers.
CREATE FUNCTION f40.emit(p_id text, p_channel text, p_bad_price boolean DEFAULT false)
RETURNS bigint LANGUAGE plpgsql AS $$
DECLARE v bigint; doc jsonb; gone boolean;
BEGIN
  IF p_channel NOT IN ('root','related') THEN RAISE EXCEPTION 'Unexpected channel'; END IF;
  INSERT INTO f40.projection_clock VALUES (p_id,1)
    ON CONFLICT(attraction_id) DO UPDATE SET revision=f40.projection_clock.revision+1
    RETURNING revision INTO v;
  doc := f40.project(p_id);
  gone := doc IS NULL;
  IF gone THEN doc := jsonb_build_object('attraction_id',p_id); END IF;
  -- Fault fixture only: a projection bug, while the business column stays bigint.
  IF p_bad_price AND NOT gone THEN
    doc := jsonb_set(doc,'{ticket_price_fen}','"broken"'::jsonb);
  END IF;
  doc := doc || jsonb_build_object('sync_revision',v,'sync_deleted',gone);
  IF p_channel='root' THEN
    INSERT INTO f40.root_event(attraction_id,revision,deleted,document) VALUES(p_id,v,gone,doc);
  ELSE
    INSERT INTO f40.related_event(attraction_id,revision,deleted,document) VALUES(p_id,v,gone,doc);
  END IF;
  RETURN v;
END $$;
INSERT INTO f40.city VALUES ('HZ','杭州'),('SZ','苏州');
INSERT INTO f40.attraction VALUES
 ('p01','西湖 游船','HZ',6000,'open',30.250,120.150),
 ('p02','西湖 步道','HZ',0,'open',30.251,120.151),
 ('p03','西湖 园林','SZ',3000,'open',31.320,120.620);
INSERT INTO f40.attraction_tag VALUES ('t01','p01','夜游'),('t02','p02','亲水');
SELECT f40.emit('p01','root'),f40.emit('p02','root'),f40.emit('p03','root');
CREATE ROLE f40_cdc LOGIN REPLICATION PASSWORD :'cdc_password';
GRANT CONNECT ON DATABASE travel_f40 TO f40_cdc;
GRANT USAGE ON SCHEMA f40 TO f40_cdc;
GRANT SELECT ON f40.root_event,f40.related_event TO f40_cdc;
CREATE PUBLICATION f40_publication FOR TABLE f40.root_event,f40.related_event;
