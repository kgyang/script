#!/usr/bin/env python

import os

def sendmail(to, subject, msg):
    import smtplib
    import email.utils
    from email.mime.text import MIMEText

    # Create the message
    mail = MIMEText(msg)
    mail['To'] = email.utils.formataddr(to)
    mail['From'] = email.utils.formataddr(('Kai YANG', 'kaigeyang@sina.com'))
    mail['Subject'] = subject
    server = smtplib.SMTP('mail')
    server.set_debuglevel(True) # show communication with the server
    try:
        server.sendmail('author@example.com', ['recipient@example.com'], msg.as_string())
    finally:
        server.quit()

if __name__ == "__main__":
    import sys
    sys.stderr.write('sendmail utility\n')
