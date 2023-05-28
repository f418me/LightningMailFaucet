

import sqlite3
import logging

from Config import Config

config = Config()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=str(config.LOG_LEVEL))
log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL_INT)

class Database(object):

    def __init__(self):
        self.__db_connection = sqlite3.connect(config.DATABASE_PATH)
        self.__db_cursor = self.__db_connection.cursor()

    def create_table(self):
        self.__db_cursor.execute('''
           CREATE TABLE IF NOT EXISTS Payee(
               email text, 
               amount integer,
               date text    
           )''')

        log.info("Database initialized successfully!!!")
        self.__db_connection.commit()

    def addPayment(self, email, amount, date):
        try:
            sqlite_insert_with_param = """INSERT INTO Payee
                              (email, amount, date) 
                              VALUES (?, ?,?);"""

            data_tuple = (email, amount, date)
            self.__db_cursor.execute(sqlite_insert_with_param, data_tuple)
            self.__db_connection.commit()
            log.info("Payment added to database")

        except sqlite3.Error as error:
            print("Failed to add payment", error)

    def getTotalAmountOfUser(self, email):

        self.__db_cursor.execute("SELECT SUM(amount) FROM Payee WHERE email=?", (email,))
        sum = self.__db_cursor.fetchone()

        if sum[0] is not None:
            amount = sum[0]
            log.debug(f'Total Payments send to User {email}: {amount}')
        else:
            log.debug(f'Until now no sats send to user {email}')
            amount = 0

        return amount

    def getTotalPayedSats(self):

        self.__db_cursor.execute("SELECT SUM(amount) FROM Payee")
        sum = self.__db_cursor.fetchone()

        if sum[0] is not None:
            amount = sum[0]
            log.debug(f'Total Sats send: {amount}')
        else:
            log.debug(f'Until now no sats send to user')
            amount = 0

        return amount


    def getNumberOfUsers(self):

        self.__db_cursor.execute("SELECT COUNT(DISTINCT email) FROM Payee")
        sum = self.__db_cursor.fetchone()

        if sum[0] is not None:
            users = sum[0]
            log.debug(f'Total Payments send: {users}')
        else:
            log.debug(f'Until now no payemens send to user')
            users =0

        return users

    def __del__(self):
        self.__db_cursor.close()
        self.__db_connection.close()