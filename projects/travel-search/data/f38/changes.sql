-- Each statement is its own committed transaction. No other writer in this lab.
INSERT INTO travel_f38.attraction VALUES
  ('p03', '西湖 花园', 'HZ', 3000, 'open', 30.252, 120.152);
UPDATE travel_f38.attraction SET ticket_price_fen = 6500 WHERE attraction_id = 'p01';
UPDATE travel_f38.attraction SET status = 'closed' WHERE attraction_id = 'p02';
