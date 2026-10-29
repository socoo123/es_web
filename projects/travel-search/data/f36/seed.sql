BEGIN;
INSERT INTO f36.city VALUES ('HZ', '杭州');
INSERT INTO f36.attraction VALUES
  ('p01', '西湖 游船', 'HZ', 6000, 'open', 30.25000, 120.15000),
  ('p02', '西湖 步道', 'HZ', 0, 'open', 30.25100, 120.15100);
INSERT INTO f36.attraction_tag VALUES
  ('p01', '亲子'), ('p01', '游船'), ('p02', '步行');
COMMIT;
