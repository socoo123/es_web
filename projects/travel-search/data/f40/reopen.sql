BEGIN;
SELECT pg_advisory_xact_lock(40040);
INSERT INTO f40.attraction VALUES ('p01','西湖 游船','HZ',7200,'open',30.250,120.150);
SELECT f40.emit('p01','root'); -- revision 6, never reset to 1
COMMIT;
