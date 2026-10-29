BEGIN;
UPDATE f36.city SET city_name = '杭州（旅游展示名）' WHERE city_code = 'HZ';
DELETE FROM f36.attraction_tag WHERE attraction_id = 'p01' AND tag = '游船';
COMMIT;
