import asyncio
import email
import imaplib
import logging
import time
import re
import csv

from aiohttp.client import ClientSession
from pylnbits.user_wallet import UserWallet
from datetime import datetime
from pylnbits.config import Config as LNBitsConfig

from mail_response import SendResponse
from config import Config
from faucet_db_operations import Database

config = Config()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=str(config.LOG_LEVEL))
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL_INT)
sendmail = SendResponse()
paytime = datetime.now()
database = Database()
database.create_table()

csv_file    = 'blocked_mail_provider.csv'

def extract_lightning_invoice_from_email(email_content):
    msg = email.message_from_string(email_content)

    # Prüfen, ob die E-Mail mehrere Teile hat
    if msg.is_multipart():
        for part in msg.walk():
            # Überprüfen, ob der Teil Text enthält
            if part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html':
                text = part.get_payload(decode=True).decode()
                lightning_invoice = extract_lightning_invoice_from_text(text)
                if lightning_invoice:
                    return lightning_invoice
    else:
        # Wenn die E-Mail nur einen Teil hat
        text = msg.get_payload(decode=True).decode()
        lightning_invoice = extract_lightning_invoice_from_text(text)
        if lightning_invoice:
            return lightning_invoice
        else:
            lightning_invoice = extract_lightning_lnurlp_from_text(text)
            return lightning_invoice

    return None


def extract_lightning_lnurlp_from_text(text):
    message_str = text[text.find('lnurl'):]
    # split the string into lines
    lines = message_str.splitlines()
    # take the first line
    ln_invoice = lines[0] if lines else None
    ln_invoice = trim_invoice_string(ln_invoice) if ln_invoice else None
    return ln_invoice


def extract_lightning_invoice_from_text(text):
    message_str = text[text.find('lnbc'):]
    # split the string into lines
    lines = message_str.splitlines()
    # take the first line
    ln_invoice = lines[0] if lines else None
    ln_invoice = trim_invoice_string(ln_invoice) if ln_invoice else None
    return ln_invoice


def trim_invoice_string(s):
    # Checks if there's an uppercase letter in the first 30 characters
    if not re.search(r'[A-Z]', s[:30]):
        # If no uppercase letter is found, it searches for an uppercase letter in the entire string
        match = re.search(r'[A-Z]', s)
        if match:
            # If an uppercase letter is found, the code cuts the string starting from that uppercase letter
            return s[:match.start()]

    # If there's an uppercase letter in the first 30 characters or if no uppercase letter is found in the entire string, the original string is returned
    return s

def check_email_domain(email, domain_list):
    email_domain = email.split('@')[-1]
    email_domain = email_domain.split('>', 1)[0] if '>' in email_domain else email_domain
    log.info(f"email_domain: {email_domain}")
    if email_domain in domain_list:
        return False
    else:
        return True


async def main():
    # INITIALIZE the pylnbits with your config file
    c = LNBitsConfig(in_key=config.LNBITS_IN_KEY, admin_key=config.LNBITS_ADMIN_KEY, lnbits_url=config.LNBITS_URL)
    url = c.lnbits_url
    log.debug(f"url: {url}")
    log.debug(f"headers: {c.headers()}")
    log.debug(f"admin_headers: {c.admin_headers()}")

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        domain_list = [row[0] for row in reader]

    async with ClientSession() as session:
        # GET wallet details
        uw = UserWallet(c, session)
        user_wallet = await uw.get_wallet_details()
        log.info(f"user wallet info : {user_wallet}")

        # Reading E-Mails as documented and described unter:
        # https://humberto.io/blog/sending-and-receiving-emails-with-python/
        while True:

            try:
                mail = imaplib.IMAP4_SSL(config.MAIL_SERVER)
                mail.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
                mail.select('inbox')

                #status, data = mail.search(None, 'ALL')
                status, data = mail.search(None, '(UNSEEN)')
            except:
                log.error('Problem connecting Mailbox - we try again!')


            # the list returned is a list of bytes separated
            # by white spaces on this format: [b'1 2 3', b'4 5 6']
            # so, to separate it first we create an empty list
            mail_ids = []
            # then we go through the list splitting its blocks
            # of bytes and appending to the mail_ids list
            for block in data:
                # the split function called without parameter
                # transforms the text or bytes into a list using
                # as separator the white spaces:
                # b'1 2 3'.split() => [b'1', b'2', b'3']
                mail_ids += block.split()

            for i in mail_ids:

                status, data = mail.fetch(i, '(RFC822)')

                # the content data at the '(RFC822)' format comes on
                # a list with a tuple with header, content, and the closing
                # byte b')'
                for response_part in data:
                    # so if its a tuple...
                    if isinstance(response_part, tuple):
                        # we go for the content at its second element
                        # skipping the header at the first and the closing
                        # at the third
                        message = email.message_from_bytes(response_part[1])

                        mail_from = message['from']
                        mail_subject = message['subject']

                        # We need also the plain e-mail address
                        match = re.search(r'<(.*?)>', mail_from)

                        if match:
                            email_only = match.group(1)
                        else:
                            email_only = mail_from

                        log.info(f'From: {mail_from}')
                        log.info(f'EMail only: {email_only}')
                        log.info(f'Subject: {mail_subject}')

                        if check_email_domain(mail_from, domain_list):
                            log.info('Domain is allowed')
                            # Since messages from different mail clients can be
                            message_str = str(message)

                            # Extract the Lightning Invoice from the message
                            ln_invoice = ''
                            ln_invoice = extract_lightning_invoice_from_email(message_str)
                            str(ln_invoice)
                            if ln_invoice is not None and ln_invoice.startswith('lnbc'):
                                log.info("Lightning Invoice found:")
                                log.info(ln_invoice)
                            else:
                                log.info('Mail contains no Lightning Invoice')
                                ln_invoice = ''

                            log.info(f'Clean LN Invoice:' + ln_invoice)
                            decoded = await uw.get_decoded(ln_invoice)
                            log.debug(decoded)

                            if 'message' in decoded:
                                if decoded['message'] == 'Failed to decode':
                                    logging.warning(F'Invoice decoding failed with message: ' + decoded['message'])
                                    is_valid = False
                            else:
                                is_valid = True

                            if is_valid:
                                amount = 0
                                amount_of_user = database.getTotalAmountOfUser(email_only)
                                if 'amount_msat' in decoded:
                                    amount = int(int(decoded['amount_msat']) / 1000)
                                if amount == 0:
                                    log.info('Amount 0 or not set: ' + str(amount))
                                    sendmail.send_response(mail_from, 'AMOUNT_ZERO',
                                                           database.getTotalAmountOfUser(email_only),
                                                           database.getTotalPayedSats(), database.getNumberOfUsers())
                                elif amount_of_user + amount <= int(config.MAX_AMOUNT):
                                    bolt = ln_invoice
                                    body = {"out": True, "bolt11": bolt}
                                    res = await uw.pay_invoice(True, bolt)

                                    if 'payment_hash' in res:
                                        database.addPayment(email_only, amount, datetime.now())
                                        sendmail.send_response(mail_from, 'SUCCESSFUL',
                                                               database.getTotalAmountOfUser(email_only),
                                                               database.getTotalPayedSats(),
                                                               database.getNumberOfUsers())
                                    else:
                                        sendmail.send_response(mail_from, 'WRONG',
                                                               0,
                                                               0, 0)

                                else:
                                    log.debug('Amount to high: ' + str(amount))
                                    sendmail.send_response(mail_from, 'AMOUNT_TO_HIGH',
                                                           database.getTotalAmountOfUser(email_only),
                                                           database.getTotalPayedSats(), database.getNumberOfUsers())

                        else:
                            log.info('Domain is NOT allowed')
                            sendmail.send_response(mail_from, 'NOT_ALLOWED',
                                                   0,
                                                   0, 0)
                    else:
                        log.info('No Payment done')
                        sendmail.send_response(mail_from, 'WRONG',
                                               0,
                                               0, 0)

            time.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
