-- 仍在相同 REPEATABLE READ 事务中，第二次导出应与第一次一致。
\o /tmp/f36-snapshot-again.ndjson
\i /lesson/export.sql
\o
COMMIT;
