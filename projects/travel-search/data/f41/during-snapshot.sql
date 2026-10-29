BEGIN;
SELECT pg_advisory_xact_lock(41041);
UPDATE f41.attraction SET ticket_price_fen=6500 WHERE attraction_id='p01';
SELECT f41.emit('p01'); -- revision 2
DELETE FROM f41.attraction WHERE attraction_id='p02';
SELECT f41.emit('p02'); -- revision 2, retained deletion marker
INSERT INTO f41.attraction VALUES('p04','西湖 夜游','HZ',4500,'open',30.252,120.152);
SELECT f41.emit('p04'); -- revision 1
UPDATE f41.city SET city_name='杭州城区' WHERE city_code='HZ';
SELECT f41.emit(attraction_id) FROM f41.attraction WHERE city_code='HZ' ORDER BY attraction_id;
-- p01 revision 3; p04 revision 2, both complete projections.
COMMIT;
