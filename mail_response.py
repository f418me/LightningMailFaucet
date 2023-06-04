from smtplib import SMTP_SSL
from pathlib import Path

from redmail import EmailSender, gmail
import logging
from config import Config


# Todo https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
config = Config()
logging.basicConfig(filename='LNMailFaucet.log', format='%(asctime)s - %(levelname)s - %(message)s', level=str(config.LOG_LEVEL))
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL_INT)

class SendResponse:


    def send_response(self,to_address, message_type, user_amount, total_amount, number_of_users):
        to_emails = [to_address]
        log.debug('Send Mail Respose')
        with open('mail_style.css') as f:
            css_content = f.readlines()
        css_string = ''.join(css_content)

        if message_type == 'SUCCESSFUL':
            log.debug('Send SUCCESSFUL Message')
            subject = 'Payment successful'
            with open('success_message.html') as f:
                html_content = f.readlines()
        elif message_type == 'AMOUNT_TO_HIGH':
            subject = 'Amount to high'
            with open('amount_to_high_message.html') as f:
                html_content = f.readlines()
        elif message_type == 'AMOUNT_ZERO':
            subject = 'Invoice amount is not set or zero'
            with open('amount_zero_message.html') as f:
                html_content = f.readlines()
        elif message_type == 'MAX_AMOUNT':
            subject = 'Amount of invoice to high!'
            with open('max_amount_message.html') as f:
                html_content = f.readlines()
        else:
            subject = 'Sorry, something went wrong!'
            with open('failure_message.html') as f:
                html_content = f.readlines()

        html_string = ''.join(html_content)

        if config.USE_GMAIL_TO_SEND_MAIL:
            gmail.username = config.GMAIL_USERNAME
            gmail.password = config.GOOGLE_APP_PW

            gmail.send(
                subject=subject,
                sender=gmail.username,
                receivers=to_emails,
                html=html_string,
                body_images={
                    'logo': 'f418me_200.jpg'
                },
                body_params={
                    'user_amount': user_amount,
                    'total_amount': total_amount,
                    'number_of_users': number_of_users,
                    'max_amount': config.MAX_AMOUNT,
                    'css': css_string,
                }
            )
        else:
            email = EmailSender(
                host=config.MAIL_SERVER,
                port=465,
                cls_smtp=SMTP_SSL,
                use_starttls=False,
                username=config.EMAIL_ADDRESS,
                password=config.EMAIL_PASSWORD
            )

            email.send(
                subject=subject,
                sender=config.EMAIL_ADDRESS,
                receivers=to_emails,
                html= html_string,
                body_images={
                    'logo': 'f418me_200.jpg',

                },
                body_params={
                    'user_amount': user_amount,
                    'total_amount': total_amount,
                    'number_of_users': number_of_users,
                    'max_amount': config.MAX_AMOUNT,
                    'css': css_string,
                }
            )
        


