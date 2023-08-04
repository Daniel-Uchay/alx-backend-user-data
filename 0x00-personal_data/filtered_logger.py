#!/usr/bin/env python3
"""ALX SE Regex-ing"""
from typing import List
import re
import logging
import mysql.connector
import os


PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """Returns an obfuscated log message passed in message"""
    for pattern in fields:
        regex_pattern = r'({}=).*?({})'.format(pattern, separator)
        message = re.sub(regex_pattern, r'\1{}\2'.format(redaction), message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """Initialize the class"""
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """filter values in incoming log records using filter_datum()"""
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.getMessage(), self.SEPARATOR)
        return super().format(record)


def get_logger() -> logging.Logger:
    """Returns a new log object"""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)

    logger.propagate = False

    fmt = RedactingFormatter(PII_FIELDS)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Connects to mysql database"""
    DB_HOST = os.environ.get('PERSONAL_DATA_DB_HOST')
    DB_USER = os.environ.get('PERSONAL_DATA_DB_USERNAME')
    DB_PASSWORD = os.environ.get('PERSONAL_DATA_DB_PASSWORD')
    DB_NAME = os.environ.get('PERSONAL_DATA_DB_NAME')

    return mysql.connector.connect(host=DB_HOST, user=DB_USER,
                                   password=DB_PASSWORD, database=DB_NAME)


def main() -> None:
    """Main function"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    fmt = RedactingFormatter(PII_FIELDS)
    for (name, email, phone, ssn, password, ip, last_login,
         user_agent) in cursor:
        message = (
            f'name={name};email={email};phone={phone};ssn={ssn}'
            f'password={password};ip={ip};'
            f'last_login={last_login};user_agent={user_agent};'
        )
        logger = logging.LogRecord('user_data', logging.INFO, None, None,
                                   message, None, None)

        print(fmt.format(logger))

    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
