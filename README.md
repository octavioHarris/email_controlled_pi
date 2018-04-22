# email_controlled_pi

Requirements:
- internet connection
- settings.ini file in the main directory

# Format of settings.ini

[CONNECTION]                             
EMAIL=EMAIL_TO_USE
PASSWORD=PASSWORD_TO_USE
IMAP_SERVER=EMAIL_IMAP_SERVER (e.g. imap.gmail.com)
SMTP_SERVER=EMAIL_SMTP_SERVER (e.g. smtp.gmail.com)
SMTP_PORT=EMAIL_SMTP_SERVER_PORT (e.g. 465 for gmail)

[PROGRAM]
READ_INTERVAL=INBOX_POLLING_INTERVAL (in seconds)
LAST_PROCESSED_ID_FILE=FILE_CONTAINING_ID_OF_LAST_PROCESSED_EMAIL

[EVENT_LOGGING]
EVENT_REPORT_EMAIL=EMAIL_TO_SPAM_WITH_EVENTS
EVENT_LOG_FILE=FILE_TO_STORE_EVENTS (json)
