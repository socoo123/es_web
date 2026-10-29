BEGIN;
UPDATE f39.city SET city_name='杭州城区' WHERE city_code='HZ';
UPDATE f39.attraction SET ticket_price_fen=6500 WHERE attraction_id='p01';
INSERT INTO f39.attraction_tag VALUES ('t04','p03','亲子');
COMMIT;
