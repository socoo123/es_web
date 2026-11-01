BEGIN;
UPDATE f45.attractions
SET ticket_price_fen = 4500, sync_revision = 2 WHERE attraction_id = 'n01';
SELECT f45.emit('n01');
UPDATE f45.attractions
SET status = 'closed', sync_deleted = true, sync_revision = 2
WHERE attraction_id = 'n02';
SELECT f45.emit('n02');
COMMIT;
