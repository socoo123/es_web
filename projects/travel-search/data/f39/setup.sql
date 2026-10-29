-- Secrets are bound by lab.py through psql stdin, never committed or logged.
CREATE SCHEMA f39;
CREATE TABLE f39.city (
  city_code text PRIMARY KEY,
  city_name text NOT NULL
);
CREATE TABLE f39.attraction (
  attraction_id text PRIMARY KEY CHECK (attraction_id ~ '^p[0-9]{2}$'),
  name text NOT NULL,
  city_code text NOT NULL REFERENCES f39.city(city_code),
  ticket_price_fen bigint NOT NULL CHECK (ticket_price_fen >= 0),
  status text NOT NULL CHECK (status IN ('open', 'closed')),
  latitude double precision NOT NULL,
  longitude double precision NOT NULL
);
CREATE INDEX ON f39.attraction(city_code);
CREATE TABLE f39.attraction_tag (
  tag_id text PRIMARY KEY CHECK (tag_id ~ '^t[0-9]{2}$'),
  attraction_id text NOT NULL REFERENCES f39.attraction(attraction_id) ON DELETE CASCADE,
  tag text NOT NULL,
  UNIQUE (attraction_id, tag)
);
CREATE INDEX ON f39.attraction_tag(attraction_id);
INSERT INTO f39.city VALUES ('HZ','杭州'), ('SZ','苏州');
INSERT INTO f39.attraction VALUES
  ('p01','西湖 游船','HZ',6000,'open',30.250,120.150),
  ('p02','西湖 步道','HZ',0,'open',30.251,120.151),
  ('p03','西湖 园林','SZ',3000,'open',31.320,120.620);
INSERT INTO f39.attraction_tag VALUES
  ('t01','p01','亲水'), ('t02','p01','夜游'), ('t03','p02','亲水');
-- FULL is essential for the non-key old attraction_id of a moved/deleted tag.
ALTER TABLE f39.city REPLICA IDENTITY FULL;
ALTER TABLE f39.attraction REPLICA IDENTITY FULL;
ALTER TABLE f39.attraction_tag REPLICA IDENTITY FULL;
CREATE ROLE f39_cdc LOGIN REPLICATION PASSWORD :'cdc_password';
CREATE ROLE f39_projector LOGIN PASSWORD :'projector_password';
GRANT CONNECT ON DATABASE travel_f39 TO f39_cdc, f39_projector;
GRANT USAGE ON SCHEMA f39 TO f39_cdc, f39_projector;
GRANT SELECT ON ALL TABLES IN SCHEMA f39 TO f39_cdc, f39_projector;
CREATE PUBLICATION f39_publication FOR TABLE f39.city, f39.attraction, f39.attraction_tag;
