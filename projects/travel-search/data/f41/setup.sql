-- psql binds cdc_password through stdin; no credentials in this file.
CREATE SCHEMA f41;
CREATE TABLE f41.city (city_code text PRIMARY KEY, city_name text NOT NULL);
CREATE TABLE f41.attraction (
  attraction_id text PRIMARY KEY CHECK (attraction_id ~ '^p[0-9]{2}$'),
  name text NOT NULL, city_code text NOT NULL REFERENCES f41.city,
  ticket_price_fen bigint NOT NULL CHECK (ticket_price_fen >= 0),
  status text NOT NULL CHECK (status IN ('open','closed')),
  latitude double precision NOT NULL, longitude double precision NOT NULL
);
CREATE TABLE f41.attraction_tag (
  tag_id text PRIMARY KEY, attraction_id text NOT NULL REFERENCES f41.attraction ON DELETE CASCADE,
  tag text NOT NULL, UNIQUE(attraction_id,tag)
);
-- Preserve clocks for closed/deleted roots, including during full export.
CREATE TABLE f41.projection_clock (attraction_id text PRIMARY KEY, revision bigint NOT NULL CHECK (revision > 0));
CREATE TABLE f41.projection_event (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  kind text NOT NULL CHECK (kind IN ('document','fence')),
  attraction_id text, revision bigint, document jsonb, fence_key text UNIQUE,
  CHECK ((kind='document' AND attraction_id IS NOT NULL AND revision > 0 AND document IS NOT NULL AND fence_key IS NULL)
      OR (kind='fence' AND attraction_id IS NULL AND revision IS NULL AND document IS NULL AND fence_key IS NOT NULL))
);
CREATE FUNCTION f41.project(p_id text) RETURNS jsonb LANGUAGE sql STABLE AS $$
  SELECT jsonb_build_object(
    'attraction_id',a.attraction_id,'name',a.name,'city_code',a.city_code,'city_name',c.city_name,
    'ticket_price_fen',a.ticket_price_fen,'currency','CNY','status',a.status,
    'location',jsonb_build_object('lat',a.latitude,'lon',a.longitude),
    'tags',COALESCE((SELECT jsonb_agg(t.tag ORDER BY t.tag COLLATE "C")
                    FROM f41.attraction_tag t WHERE t.attraction_id=a.attraction_id),'[]'::jsonb))
  FROM f41.attraction a JOIN f41.city c USING(city_code)
  WHERE a.attraction_id=p_id AND a.status='open'
$$;
CREATE FUNCTION f41.envelope(p_id text) RETURNS jsonb LANGUAGE sql STABLE AS $$
  SELECT COALESCE(f41.project(p_id),jsonb_build_object('attraction_id',p_id))
    || jsonb_build_object('sync_revision',revision,'sync_deleted',f41.project(p_id) IS NULL)
  FROM f41.projection_clock WHERE attraction_id=p_id
$$;
-- Every writer takes lock 41041 BEFORE changing business rows. No trigger
-- enforces this for arbitrary writers. Emit ALL affected roots in the same tx.
CREATE FUNCTION f41.emit(p_id text) RETURNS bigint LANGUAGE plpgsql AS $$
DECLARE v bigint;
BEGIN
  INSERT INTO f41.projection_clock VALUES(p_id,1)
    ON CONFLICT(attraction_id) DO UPDATE SET revision=f41.projection_clock.revision+1
    RETURNING revision INTO v;
  INSERT INTO f41.projection_event(kind,attraction_id,revision,document)
    VALUES('document',p_id,v,f41.envelope(p_id));
  RETURN v;
END $$;
INSERT INTO f41.city VALUES('HZ','杭州'),('SZ','苏州');
INSERT INTO f41.attraction VALUES
 ('p01','西湖 游船','HZ',6000,'open',30.250,120.150),
 ('p02','西湖 步道','HZ',0,'open',30.251,120.151),
 ('p03','西湖 园林','SZ',3000,'open',31.320,120.620);
INSERT INTO f41.attraction_tag VALUES('t01','p01','夜游'),('t02','p02','亲水');
SELECT f41.emit('p01'),f41.emit('p02'),f41.emit('p03');
CREATE ROLE f41_cdc LOGIN REPLICATION PASSWORD :'cdc_password';
GRANT CONNECT ON DATABASE travel_f41 TO f41_cdc;
GRANT USAGE ON SCHEMA f41 TO f41_cdc;
GRANT SELECT ON f41.projection_event TO f41_cdc;
CREATE PUBLICATION f41_publication FOR TABLE f41.projection_event;
