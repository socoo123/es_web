-- Bind fence_key through psql stdin. Same lock as EVERY cooperating writer.
BEGIN;
SELECT pg_advisory_xact_lock(42042);
INSERT INTO f42.projection_event(kind,fence_key) VALUES('fence',:'fence_key');
SELECT jsonb_build_object('fence_key',:'fence_key','documents',
  (SELECT jsonb_agg(f42.envelope(attraction_id)::text ORDER BY attraction_id)
   FROM f42.projection_clock));
COMMIT;
