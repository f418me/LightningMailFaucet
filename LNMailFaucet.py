import asyncio
import email
import imaplib
import logging
import time
import re

from aiohttp.client import ClientSession
from pylnbits.user_wallet import UserWallet
from datetime import datetime
from pylnbits.config import Config as LNBitsConfig

from SendResponse import SendResponse
from Config import Config
from faucet_db_operations import Database

config = Config()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=str(config.LOG_LEVEL))
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL_INT)
sendmail = SendResponse()
paytime = datetime.now()
database = Database()
database.create_table()


async def main():
    # INITIALIZE the pylnbits with your config file
    c = LNBitsConfig(in_key=config.LNBITS_IN_KEY, admin_key=config.LNBITS_ADMIN_KEY, lnbits_url=config.LNBITS_URL)
    url = c.lnbits_url
    log.debug(f"url: {url}")
    log.debug(f"headers: {c.headers()}")
    log.debug(f"admin_headers: {c.admin_headers()}")

    async with ClientSession() as session:
        # GET wallet details
        uw = UserWallet(c, session)
        user_wallet = await uw.get_wallet_details()
        log.info(f"user wallet info : {user_wallet}")

        while True:
            mail = imaplib.IMAP4_SSL(config.MAIL_SERVER)
            mail.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            mail.select('inbox')

            # status, data = mail.search(None, 'ALL')
            status, data = mail.search(None, '(UNSEEN)')

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

            # now for every id we'll fetch the email
            # to extract its content
            for i in mail_ids:
                # the fetch function fetch the email given its id
                # and format that you want the message to be
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

                        # with the content we can extract the info about
                        # who sent the message and its subject
                        mail_from = message['from']
                        mail_subject = message['subject']

                        # Suche nach Übereinstimmungen mit dem regulären Ausdruck
                        match = re.search(r'<(.*?)>', mail_from)

                        # Extrahiere den gefundenen Text
                        if match:
                            email_only = match.group(1)
                        else:
                            email_only = mail_from

                        ln_invoice = str(message)

                        # Remove everything before lnbc
                        ln_invoice = ln_invoice[ln_invoice.find('lnbc'):]

                        # todo check different line breaks
                        # Remove everything after linebreak
                        pattern = r"=\n"
                        ln_invoice = re.sub(pattern, "", ln_invoice)
                        ln_invoice = ln_invoice.split('\n', 1)[0]

                        # and then let's show its result
                        logging.info(f'From: {mail_from}')
                        logging.info(f'EMail only: {email_only}')
                        logging.info(f'Subject: {mail_subject}')

                        # Remove everything after linebreak
                        # todo wie ich machen, dass nur die Split nach dem gleich heraus genommen werden.
                        # ln_invoice = ln_invoice.split('>', 1)[0]
                        # ln_invoice = ln_invoice.split('\r\n', 1)[0]
                        # ln_invoice = ln_invoice.split('\n', 1)[0]

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
                            if 'amount_msat' in decoded:
                                amount = int(int(decoded['amount_msat']) / 1000)
                            if amount == 0:
                                log.info('Amount 0 or not specificated: ' + str(amount))
                                sendmail.send_response(mail_from, 'AMOUNT_ZERO',
                                                       database.getTotalAmountOfUser(email_only),
                                                       database.getTotalPayedSats(), database.getNumberOfUsers())
                            elif amount <= int(config.MAX_AMOUNT):
                                log.info('Amount lower than total max: ' + str(amount))
                                amount_of_user = database.getTotalAmountOfUser(email_only)

                                if amount_of_user + amount >= int(config.MAX_AMOUNT):
                                    sendmail.send_response(mail_from, 'AMOUNT_TO_HIGH',
                                                           database.getTotalAmountOfUser(email_only),
                                                           database.getTotalPayedSats(), database.getNumberOfUsers())
                                else:
                                    bolt = ln_invoice
                                    body = {"out": True, "bolt11": bolt}
                                    res = await uw.pay_invoice(True, bolt)

                                    if 'payment_hash' in res:
                                        database.addPayment(email_only, amount, datetime.now())
                                        sendmail.send_response(mail_from, 'SUCCESSFUL',
                                                               database.getTotalAmountOfUser(email_only),
                                                               database.getTotalPayedSats(), database.getNumberOfUsers())
                                    else:
                                        sendmail.send_response(mail_from, 'WRONG',
                                                               0,
                                                               0, 0)

                            else:
                                log.debug('Amount to high: ' + str(amount))
                                sendmail.send_response(mail_from, 'MAX_AMOUNT',
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
