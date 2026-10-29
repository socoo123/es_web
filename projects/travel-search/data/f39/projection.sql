SELECT a.attraction_id AS id,
       jsonb_build_object(
         'attraction_id', a.attraction_id, 'name', a.name,
         'city_code', a.city_code, 'city_name', c.city_name,
         'ticket_price_fen', a.ticket_price_fen, 'currency', 'CNY', 'status', a.status,
         'location', jsonb_build_object('lat', a.latitude, 'lon', a.longitude),
         'tags', COALESCE((SELECT jsonb_agg(t.tag ORDER BY t.tag COLLATE "C")
                           FROM f39.attraction_tag t WHERE t.attraction_id=a.attraction_id), '[]'::jsonb)
       ) AS document
FROM f39.attraction a JOIN f39.city c USING (city_code)
WHERE a.status='open'
ORDER BY a.attraction_id;
