-- t04 is removed by the FK cascade; both tables emit real delete events.
DELETE FROM f39.attraction WHERE attraction_id='p03';
