#!/usr/bin/python
import json
import traceback

from event_logging import EventLogger
from email_utils import EmailConnection, EmailListener

import master.app as master
import stable.app as stable

SETTINGS_FILE_PATH = 'settings.json'

def open_email_connection(settings):
   
    connection_settings = settings['CONNECTION']

    # Extract connection settings
    email       = connection_settings['EMAIL']
    password    = connection_settings['PASSWORD']
    imap_server = connection_settings['IMAP_SERVER']
    smtp_server = connection_settings['SMTP_SERVER']
    smtp_port   = connection_settings['SMTP_PORT']

    # Open and return the email connection
    return EmailConnection(imap_server, smtp_server, email, password)

def create_event_logger(connection, settings):

    event_logging_settings = settings['EVENT_LOGGING']

    # Extract event logging setings
    event_log_file      = event_logging_settings['EVENT_LOG_FILE']
    event_report_email  = event_logging_settings['EVENT_REPORT_EMAIL']

    # Initialize and return the event logger
    return EventLogger(connection, event_log_file, event_report_email)

def create_email_listener(connection, event_logger, settings):
 
    # Extract program settings 
    read_interval = float(settings['PROGRAM']['READ_INTERVAL'])
 
    # Start email listener
    return EmailListener(connection, event_logger, read_interval)

def run_version(version_module, version_name, connection, listener, event_logger, settings):
 
    try:

        # Reload the module 
        version_module = reload(version_module)        
        
        # Run the module
        event_logger.log_event('Watchdog: STARTING ' + version_name, '') 
        version_module.run(connection, listener, settings)
        event_logger.log_event('Watchdog: SAFELY TERMINATED ' + version_name, '')
        return True

    except Exception:

        # Record crash details and switch back to stable version
        crash_details = traceback.format_exc()
        event_logger.log_event('Watchdog: CRASH on ' + version_name, crash_details)
        return False
      
def main():
   
    # Read from settings.json file
    with open(SETTINGS_FILE_PATH) as file:        
        settings = json.load(file)

    # Open the connection, create an event_logger and then an email_listener
    connection = open_email_connection(settings)
    event_logger = create_event_logger(connection, settings)
    listener = create_email_listener(connection, event_logger, settings)

    # Send any previously logged events
    event_logger.send_email_report()

    # Automatically restart master version when it exits safely
    while run_version(master, 'master', connection, listener, event_logger, settings): pass
    
    # Fall back on stable version
    run_version(stable, 'stable', connection, listener, event_logger, settings)
        
if __name__ == "__main__":
    main()

