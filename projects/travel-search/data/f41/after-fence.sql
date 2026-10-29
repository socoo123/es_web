-- Accepted while both consumers are deliberately stopped at the cutover fence.
BEGIN;
SELECT pg_advisory_xact_lock(41041);
UPDATE f41.attraction SET ticket_price_fen=7200 WHERE attraction_id='p01';
SELECT f41.emit('p01'); -- revision 5
DELETE FROM f41.attraction WHERE attraction_id='p04';
SELECT f41.emit('p04'); -- revision 4
COMMIT;
