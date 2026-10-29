-- 本课受控事务明确改了这三个 ID；不是从日志自动捕获的变更清单。
SELECT jsonb_build_object('op', op, 'id', id, 'document', document)
FROM f36.search_projection WHERE id IN ('p01', 'p02', 'p03') ORDER BY id;
