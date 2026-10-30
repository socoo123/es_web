-- Caller created repair_expected(value jsonb), an array of canonical JSON texts.
-- Keep the transaction lock until ALL affected IDs have emitted new revisions.
DO $$
BEGIN
  IF (SELECT jsonb_agg(f42.envelope(attraction_id)::text ORDER BY attraction_id)
      FROM f42.projection_clock)
     IS DISTINCT FROM (SELECT value FROM repair_expected) THEN
    RAISE EXCEPTION 'stale repair plan: current source differs; audit again';
  END IF;
END $$;
