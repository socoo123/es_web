CREATE SCHEMA f45;
CREATE TABLE f45.attractions (
  attraction_id text PRIMARY KEY, name text NOT NULL, city_code text NOT NULL,
  currency text NOT NULL, status text NOT NULL, accessible boolean NOT NULL,
  visit_minutes integer NOT NULL, location jsonb NOT NULL,
  sync_revision bigint NOT NULL, sync_deleted boolean NOT NULL,
  ticket_price_fen bigint NOT NULL
);
CREATE TABLE f45.projection_event (
  event_id bigserial PRIMARY KEY, attraction_id text NOT NULL,
  revision bigint NOT NULL, document text NOT NULL
);
CREATE FUNCTION f45.emit(id text) RETURNS void LANGUAGE sql AS $$
  INSERT INTO f45.projection_event(attraction_id, revision, document)
  SELECT attraction_id, sync_revision, row_to_json(a)::text
  FROM f45.attractions a WHERE attraction_id = id;
$$;
CREATE PUBLICATION f45_publication FOR TABLE f45.projection_event;
GRANT USAGE ON SCHEMA f45 TO f45_cdc;
GRANT SELECT ON f45.projection_event TO f45_cdc;
