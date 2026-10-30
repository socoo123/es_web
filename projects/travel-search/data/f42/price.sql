BEGIN;
SELECT pg_advisory_xact_lock(42042);
UPDATE f42.attraction SET ticket_price_fen=6500 WHERE attraction_id='p01';
SELECT f42.emit('p01');
COMMIT;
