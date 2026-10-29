CREATE VIEW f36.search_projection AS
SELECT a.attraction_id AS id,
       CASE WHEN a.status = 'open' THEN 'index' ELSE 'delete' END AS op,
       CASE WHEN a.status = 'open' THEN jsonb_build_object(
         'attraction_id', a.attraction_id,
         'name', a.name,
         'city_code', a.city_code,
         'city_name', c.city_name,
         'ticket_price_fen', a.ticket_price_fen,
         'currency', 'CNY',
         'status', a.status,
         'location', jsonb_build_object('lat', a.latitude, 'lon', a.longitude),
         'tags', COALESCE((SELECT jsonb_agg(t.tag ORDER BY t.tag COLLATE "C")
                           FROM f36.attraction_tag t
                           WHERE t.attraction_id = a.attraction_id), '[]'::jsonb)
       ) ELSE NULL END AS document
FROM f36.attraction a
JOIN f36.city c ON c.city_code = a.city_code;
