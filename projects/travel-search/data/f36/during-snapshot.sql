BEGIN;
UPDATE f36.attraction SET ticket_price_fen = 6500 WHERE attraction_id = 'p01';
UPDATE f36.attraction SET status = 'closed' WHERE attraction_id = 'p02';
INSERT INTO f36.attraction VALUES
  ('p03', '西湖 湿地', 'HZ', 3000, 'open', 30.25200, 120.15200);
INSERT INTO f36.attraction_tag VALUES ('p03', '观鸟');
COMMIT;
