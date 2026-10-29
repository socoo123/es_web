-- Administrator creates this publication; the CDC login is not an owner.
CREATE SCHEMA f37;
CREATE TABLE f37.attraction (
  attraction_id text PRIMARY KEY CHECK (attraction_id ~ '^p[0-9]{2}$'),
  name text NOT NULL,
  city_code text NOT NULL,
  ticket_price_fen bigint NOT NULL CHECK (ticket_price_fen >= 0),
  status text NOT NULL CHECK (status IN ('open', 'closed')),
  latitude double precision NOT NULL,
  longitude double precision NOT NULL
);
INSERT INTO f37.attraction VALUES
  ('p01', '西湖 游船', 'HZ', 6000, 'open', 30.250, 120.150),
  ('p02', '西湖 步道', 'HZ', 0, 'open', 30.251, 120.151);
CREATE ROLE f37_cdc LOGIN REPLICATION PASSWORD :'cdc_password';
GRANT CONNECT ON DATABASE travel_f37 TO f37_cdc;
GRANT USAGE ON SCHEMA f37 TO f37_cdc;
GRANT SELECT ON f37.attraction TO f37_cdc;
CREATE PUBLICATION f37_publication FOR TABLE f37.attraction;
