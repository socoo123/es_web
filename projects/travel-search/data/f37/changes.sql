-- Each statement is its own committed transaction. No other writer in this lab.
INSERT INTO f37.attraction VALUES
  ('p03', '西湖 花园', 'HZ', 3000, 'open', 30.252, 120.152);
UPDATE f37.attraction SET ticket_price_fen = 6500 WHERE attraction_id = 'p01';
UPDATE f37.attraction SET status = 'closed' WHERE attraction_id = 'p02';
