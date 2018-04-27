import re
import time
import email
import imaplib
import smtplib
import threading

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SEPARATOR_REGEX = '\r\n####'
STATUS_REPORT_ADDRESS = 'harris.octavio@gmail.com'

class EmailConnection():

    def __init__(self, imap_server, smtp_server, email, password):
        
        self.email = email
        self.imap_connection = imap_connect(imap_server, email, password)
        self.smtp_connection = smtp_connect(smtp_server, email, password)

    def fetch_email_ids(self):

        self.imap_connection.list()
        self.imap_connection.select("inbox")
        result, data = self.imap_connection.search(None, "ALL")
        email_ids = data[0].split(' ')
        return email_ids

    def fetch_email(self, email_id):

        result, data = self.imap_connection.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        return parse_email(raw_email)

    def send_email(self, to_address, subject, body):
    
        email = MIMEMultipart()
        email['From'] = self.email
        email['To'] = to_address
        email['Subject'] = subject
        email.attach(MIMEText(body, 'plain'))
        self.smtp_connection.sendmail(self.email, [to_address], email.as_string())   

    def __del__(self):
        pass
#        self.imap_connection.close()
#        self.smtp_connection.close()

class EmailListener():

    def __init__(self, connection, event_logger, poll_interval):
        
        self.connection = connection
        self.event_logger = event_logger
        self.poll_interval = poll_interval
        self.handlers = {}
        self.running = False
 
        # Only process newly received emails
        self.last_processed_id = self.connection.fetch_email_ids()[-1]

    def start(self):

        thread = threading.Thread(target = self.mainloop)
        thread.start()
        return thread
    
    def process_latest_email(self):

        # Fetch latest email
        latest_id = self.connection.fetch_email_ids()[-1]
       
        # Ensure email has not been processed already
        if latest_id != self.last_processed_id:

            body, attachments = self.connection.fetch_email(latest_id)
            self.process_message(body, attachments)
            self.last_processed_id = latest_id

    def mainloop(self, delay=time.sleep):

        self.running = True
        
        next_read_time = time.time()

        while self.running:
            
            # Poll mailbox and process latest email
            self.process_latest_email()

            # Sleep from now until next specified read time
            next_read_time += self.poll_interval
            delay(next_read_time - time.time())

    def stop(self):

        self.running = False

    def register_handler(self, key, handler):

        self.handlers[key] = handler
  
    def process_message(self, body, attachments):

        # Extract message type and text segments
        parts = re.split(SEPARATOR_REGEX, body)
        parts = map(str.strip, parts)
        message_type = parts[0].strip()
        text_segments = parts[1::]
 
        # Verify there is a configured handler for the specified message type
        if message_type not in self.handlers:
            print('Unhandled message type: ' + message_type)
            return

        print('Calling handler: ' + message_type)


        # Call the appropriate handler and stop listener if False is returned
        if self.handlers[message_type](text_segments, attachments) == False:
            self.stop()

def smtp_connect(server, email, password):

    smtp_connection = smtplib.SMTP_SSL(server, '465')
    smtp_connection.ehlo()
    smtp_connection.login(email, password)
    return smtp_connection
    
def imap_connect(server, email, password):
    
    imap_connection = imaplib.IMAP4_SSL(server)
    imap_connection.login(email, password)
    return imap_connection

def parse_email(raw_email):
 
    body = ""
    attachments = []
    
    message = email.message_from_string(raw_email)
    
    for part in message.walk():
        
        filename = part.get_filename()
            
        # Found attachment 
        if filename:
            attachments.append({
                'filename': filename,
                'binary': part.get_payload(decode=True) 
            })
            continue

        content_type = part.get_content_type()

        # Found email body 
        if content_type == 'text/plain':
            body += part.get_payload()
            continue

    return body, attachments


