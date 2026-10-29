-- Administrator creates the table. CDC credentials are bound privately through stdin.
CREATE DATABASE travel_f38 CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE TABLE travel_f38.attraction (
  attraction_id varchar(3) PRIMARY KEY,
  name varchar(100) NOT NULL,
  city_code varchar(8) NOT NULL,
  ticket_price_fen bigint NOT NULL CHECK (ticket_price_fen >= 0),
  status varchar(8) NOT NULL CHECK (status IN ('open','closed')),
  latitude double NOT NULL,
  longitude double NOT NULL
) ENGINE=InnoDB;
INSERT INTO travel_f38.attraction VALUES
  ('p01', '西湖 游船', 'HZ', 6000, 'open', 30.250, 120.150),
  ('p02', '西湖 步道', 'HZ', 0, 'open', 30.251, 120.151);
CREATE USER 'f38_cdc'@'%' IDENTIFIED BY @CDC_PASSWORD@;
GRANT SELECT ON travel_f38.* TO 'f38_cdc'@'%';
GRANT RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'f38_cdc'@'%';
