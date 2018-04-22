import json
import datetime
        
class EventLogger():

    def __init__(self, connection, log_file, log_email):
    
        self.connection = connection
        self.log_file = log_file
        self.log_email = log_email

    def log_event(self, event_type, event_details):
        
        event_date = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")    

        # Read currently logged events and append new event        
        events = self.read_log()      
        events.append({
            'type': event_type, 
            'date': event_date, 
            'details': event_details if len(event_details) > 0 else 'None'
        })

        try:
            # Try to send email report of events and clear the log
            send_email_report(self.connection, self.log_email, events)
            self.clear_log()

        except:
            # If unsuccessful, re-log all the events
            self.update_log(events)

    def send_email_report(self):

        events = self.read_log()

        if len(events) > 0:
            send_email_report(self.connection, self.log_email, events)
            self.clear_log() 

    def read_log(self):

        return read_log_file(self.log_file)
    
    def update_log(self, events):

        with open(self.log_file, 'w') as log_file:
            json.dump(events, log_file, indent=4, sort_keys=True)

    def clear_log(self):

        self.update_log([])

def read_log_file(log_file):

    with open(log_file, 'a+') as file:
        try:
            events = json.load(file)
        except: 
            events = []
    
    return [] if not isinstance(events, list) else events

def send_email_report(connection, email, events):
    
    if len(events) == 1:
        subject = events[0]['type']
    else:
        subject = str(len(events)) + ' Event(s) Reported'
        
    body = ""

    for event in events:
        body += "TYPE:\n" + event['type'] + '\n' 
        body += "DATE:\n" + event['date'] + '\n' 
        body += "DETAILS:\n" + event['details'] + '\n\n'
    
    connection.send_email(email, subject, body) 

   

