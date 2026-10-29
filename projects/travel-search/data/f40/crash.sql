BEGIN;
SELECT pg_advisory_xact_lock(40040);
UPDATE f40.attraction SET ticket_price_fen=6500 WHERE attraction_id='p01';
SELECT f40.emit('p01','root'); -- p01 revision 2, same transaction as price
COMMIT;
