-- disable sep payment provider
UPDATE payment_provider
   SET sep_terminal_id = NULL;
   SET sep_password = NULL;
