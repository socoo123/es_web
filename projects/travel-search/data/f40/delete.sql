BEGIN;
SELECT pg_advisory_xact_lock(40040);
DELETE FROM f40.attraction WHERE attraction_id='p01';
SELECT f40.emit('p01','root'); -- revision 5; clock is retained, document is a delete marker
COMMIT;
