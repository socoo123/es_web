SELECT JSON_OBJECT('version',VERSION(),'server_uuid',@@server_uuid,'server_id',@@server_id,
  'log_bin',@@log_bin,'binlog_format',@@binlog_format,'binlog_row_image',@@binlog_row_image,
  'binlog_row_value_options',@@binlog_row_value_options,
  'binlog_expire_logs_seconds',@@binlog_expire_logs_seconds,'gtid_mode',@@gtid_mode);
SHOW BINARY LOG STATUS;
SHOW BINARY LOGS;
