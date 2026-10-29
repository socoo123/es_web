BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;
-- 第一条 SELECT 固定此事务的可见视图；BEGIN 本身不是这个读边界。
SELECT current_setting('transaction_isolation') AS isolation, count(*) AS rows
FROM f36.attraction;
\o /tmp/f36-snapshot.ndjson
\i /lesson/export.sql
\o
-- 保持本会话开启。另一个终端执行 during-snapshot.sql 后，再执行 snapshot-end.sql。
