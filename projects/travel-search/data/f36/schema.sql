CREATE SCHEMA f36;
CREATE TABLE f36.city (
  city_code text PRIMARY KEY,
  city_name text NOT NULL
);
CREATE TABLE f36.attraction (
  attraction_id text PRIMARY KEY,
  name text NOT NULL,
  city_code text NOT NULL REFERENCES f36.city(city_code),
  ticket_price_fen integer NOT NULL CHECK (ticket_price_fen >= 0),
  status text NOT NULL CHECK (status IN ('open', 'closed')),
  latitude numeric(8,5) NOT NULL,
  longitude numeric(8,5) NOT NULL
);
CREATE TABLE f36.attraction_tag (
  attraction_id text NOT NULL REFERENCES f36.attraction(attraction_id),
  tag text NOT NULL,
  PRIMARY KEY (attraction_id, tag)
);
