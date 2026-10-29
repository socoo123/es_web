SELECT json_build_object(
  'current_lsn', pg_current_wal_lsn(),
  'wal_level', current_setting('wal_level'),
  'max_slot_wal_keep_size', current_setting('max_slot_wal_keep_size'),
  'slot', (SELECT row_to_json(s) FROM (
    SELECT slot_name, plugin, slot_type, database, active,
           restart_lsn, confirmed_flush_lsn, wal_status, safe_wal_size,
           pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_distance_bytes
    FROM pg_replication_slots WHERE slot_name = 'f37_slot'
  ) s)
);
