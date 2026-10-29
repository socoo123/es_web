SELECT jsonb_build_object('op', op, 'id', id, 'document', document)
FROM f36.search_projection ORDER BY id;
