BEGIN;
SELECT pg_advisory_xact_lock(41041);
UPDATE f41.attraction SET ticket_price_fen=7000 WHERE attraction_id='p01';
SELECT f41.emit('p01'); -- revision 4
UPDATE f41.attraction SET status='closed' WHERE attraction_id='p03';
SELECT f41.emit('p03'); -- revision 2, closed also becomes a marker
INSERT INTO f41.attraction_tag VALUES('t04','p04','夜景');
SELECT f41.emit('p04'); -- revision 3
COMMIT;
