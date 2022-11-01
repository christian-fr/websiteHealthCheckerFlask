import sys
import os
from email.mime.text import MIMEText
from smtplib import SMTP
from smtplib import SMTPException


def smtp_send_mail(content: str, subject: str, mail_addr: str, mail_pass: str, smtp_server: str, smtp_port: str,
              mail_to: str):

    # typical values for text_subtype are plain, html, xml
    text_subtype = 'plain'

    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject'] = subject
        msg['From'] = mail_addr  # some SMTP servers will do this automatically, not all

        conn = SMTP(smtp_server, port=int(smtp_port))
        conn.set_debuglevel(False)
        conn.login(mail_addr, mail_pass)
        try:
            conn.sendmail(mail_addr, mail_to, msg.as_string())
        finally:
            conn.quit()

    except SMTPException as err:
        sys.exit("mail failed; %s" % err)  # give an error message


if __name__ == '__main__':
    MAIL_ADDRESS = 'MAIL_ADDRESS'
    MAIL_PASS = 'MAIL_PASS'
    SMTP_SERVER = 'SMTP_SERVER'
    SMTP_PORT = 'SMTP_PORT'
    ## SMTP_AUTH = 'SMTP_AUTH'
    ## SMTP_TLS = 'SMTP_TLS'
    MAIL_TO = 'MAIL_TO'

    mail_address = os.environ[MAIL_ADDRESS]
    mail_pass = os.environ[MAIL_PASS]
    smtp_server = os.environ[SMTP_SERVER]
    smtp_port = os.environ[SMTP_PORT]
    # smtp_auth = os.environ[SMTP_AUTH]
    # smtp_tls = os.environ[SMTP_TLS]
    mail_to = os.environ[MAIL_TO]

    smtp_send_mail(content='Heyho!', subject='Test123', mail_addr=mail_address, mail_pass=mail_pass,
                   smtp_server=smtp_server, smtp_port=smtp_port, mail_to=mail_to)
