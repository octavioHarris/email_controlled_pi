import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


