BEGIN;
SELECT pg_advisory_xact_lock(41041);
UPDATE f41.attraction SET ticket_price_fen=7600 WHERE attraction_id='p01';
SELECT f41.emit('p01'); -- revision 6
INSERT INTO f41.attraction VALUES('p04','西湖 夜游','HZ',4800,'open',30.252,120.152);
SELECT f41.emit('p04'); -- revision 5; clock survives physical deletion, tags=[]
COMMIT;
