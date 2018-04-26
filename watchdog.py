#!/usr/bin/python

import master.app as master
import stable.app as stable

import traceback
import ConfigParser

from event_logging import EventLogger
from email_utils import EmailConnection, EmailListener

SETTINGS_FILE_PATH = 'settings.ini'

def open_email_connection(config):
   
    # Extract connection settings
    email       = config.get('CONNECTION', 'EMAIL')
    password    = config.get('CONNECTION', 'PASSWORD')
    imap_server = config.get('CONNECTION', 'IMAP_SERVER') 
    smtp_server = config.get('CONNECTION', 'SMTP_SERVER')
    smtp_port   = config.get('CONNECTION', 'SMTP_PORT')

    # Open and return the email connection
    return EmailConnection(imap_server, smtp_server, email, password)

def create_event_logger(connection, config):

    # Extract event logging setings
    event_log_file      = config.get('EVENT_LOGGING', 'EVENT_LOG_FILE')
    event_report_email  = config.get('EVENT_LOGGING', 'EVENT_REPORT_EMAIL')

    # Initialize and return the event logger
    return EventLogger(connection, event_log_file, event_report_email)

def create_email_listener(connection, event_logger, config):
 
    # Extract program settings 
    read_interval = float(config.get('PROGRAM', 'READ_INTERVAL'))
 
    # Start email listener
    return EmailListener(connection, event_logger, read_interval)

def run_version(version_module, version_name, email_listener, event_logger, settings):
 
    try:

        # Reload the module 
        version_module = reload(version_module)        
        
        # Run the module
        event_logger.log_event('Watchdog: STARTING ' + version_name, '') 
        version_module.run(email_listener, settings)
        event_logger.log_event('Watchdog: SAFELY TERMINATED ' + version_name, '')
        return True

    except Exception:

        # Record crash details and switch back to stable version
        crash_details = traceback.format_exc()
        event_logger.log_event('Watchdog: CRASH on ' + version_name, crash_details)
        return False
      
def main():
    
    # Read from settings.ini file
    config = ConfigParser.ConfigParser()
    config.optionxform=str 
    config.read(SETTINGS_FILE_PATH) 

    # Open the connection, create an event_logger and then an email_listener
    connection = open_email_connection(config)
    event_logger = create_event_logger(connection, config)
    email_listener = create_email_listener(connection, event_logger, config)

    # Send any previously logged events
    event_logger.send_email_report()

    # Automatically restart master version when it exits safely
    while run_version(master, 'master', email_listener, event_logger, config): pass
    
    # Fall back on stable version
    run_version(stable, 'stable', email_listener, event_logger, config)
        
if __name__ == "__main__":
    main()

