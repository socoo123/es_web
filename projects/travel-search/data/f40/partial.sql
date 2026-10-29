BEGIN;
SELECT pg_advisory_xact_lock(40040);
UPDATE f40.attraction SET ticket_price_fen=7500 WHERE attraction_id='p01';
UPDATE f40.attraction SET ticket_price_fen=1000 WHERE attraction_id='p02';
UPDATE f40.attraction SET ticket_price_fen=3200 WHERE attraction_id='p03';
SELECT f40.emit('p01','root'); -- revision 7, real success
SELECT f40.emit('p02','root',true); -- revision 3, deliberate mapping failure
SELECT f40.emit('p03','root'); -- revision 2, real success after the failed record
COMMIT;
