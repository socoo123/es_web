BEGIN;
SELECT pg_advisory_xact_lock(40040);
UPDATE f40.attraction SET ticket_price_fen=7000 WHERE attraction_id='p01';
SELECT f40.emit('p01','root'); -- revision 3, deliberately consumed later
COMMIT;
BEGIN;
SELECT pg_advisory_xact_lock(40040);
UPDATE f40.city SET city_name='杭州城区' WHERE city_code='HZ';
UPDATE f40.attraction_tag SET tag='夜景' WHERE tag_id='t01';
SELECT f40.emit('p01','related'),f40.emit('p02','related'); -- revisions 4 and 2
COMMIT;
