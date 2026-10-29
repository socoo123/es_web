-- Connect is stopped. DDL tests MySQL schema-history recovery; Java projects only its known fields.
ALTER TABLE travel_f38.attraction ADD COLUMN source_note varchar(64) NOT NULL DEFAULT 'local';
UPDATE travel_f38.attraction SET ticket_price_fen = 7000, source_note = 'binlog-after-restart'
WHERE attraction_id = 'p01';
INSERT INTO travel_f38.attraction
(attraction_id,name,city_code,ticket_price_fen,status,latitude,longitude,source_note)
VALUES ('p04','西湖 码头','HZ',1800,'open',30.253,120.153,'new-row');
DELETE FROM travel_f38.attraction WHERE attraction_id = 'p02';
