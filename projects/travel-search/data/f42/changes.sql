BEGIN;
SELECT pg_advisory_xact_lock(42042);
UPDATE f42.attraction SET ticket_price_fen=7000 WHERE attraction_id='p01';
SELECT f42.emit('p01');
DELETE FROM f42.attraction WHERE attraction_id='p02';
SELECT f42.emit('p02');
INSERT INTO f42.attraction VALUES('p04','西湖 夜游','HZ',4500,'open',30.252,120.152);
SELECT f42.emit('p04');
COMMIT;
