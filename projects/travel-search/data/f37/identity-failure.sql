-- Run only through a one-shot psql -v ON_ERROR_STOP=1 connection.
-- The DELETE errors with 55000; exiting psql rolls back the entire transaction.
BEGIN;
ALTER TABLE f37.attraction REPLICA IDENTITY NOTHING;
DELETE FROM f37.attraction WHERE attraction_id = 'p01';
ROLLBACK;
