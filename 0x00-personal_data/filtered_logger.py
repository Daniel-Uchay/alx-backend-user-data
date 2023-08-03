#!/usr/bin/env python3
"""This module defines a logging mechanism for redacting sensitive information
from log messages retrieved from a MySQL database."""

from typing import List
import mysql.connector
import logging
import re
import os


PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """Obfuscates sensitive data in a log message.

    Args:
        fields (List[str]): List of strings indicating fields to obfuscate.
        redaction (str): What the field will be obfuscated to.
        message (str): The log line to obfuscate.
        separator (str): The character separating the fields.

    Returns:
        str: The obfuscated log message.
    """
    for field in fields:
        message = re.sub(field+'=.*?'+separator,
                         field+'='+redaction+separator, message)
    return message


class RedactingFormatter(logging.Formatter):
    """Custom log formatter that redacts sensitive information from log
    messages."""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """Initialize the RedactingFormatter.

        Args:
            fields (List[str]): List of strings indicating fields to redact.
        """
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Redact the message of LogRecord instance.

        Args:
            record (logging.LogRecord): LogRecord instance containing the
            message.

        Returns:
            str: Formatted and redacted log message.
        """
        message = super(RedactingFormatter, self).format(record)
        redacted = filter_datum(self.fields, self.REDACTION,
                                message, self.SEPARATOR)
        return redacted


def get_logger() -> logging.Logger:
    """Returns a logging.Logger object configured to redact sensitive
    information.

    Returns:
        logging.Logger: Logger object with the redacting formatter.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler()

    formatter = RedactingFormatter(PII_FIELDS)

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Establish a connection to the MySQL database.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection.
    """
    user = os.getenv('PERSONAL_DATA_DB_USERNAME') or "root"
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD') or ""
    host = os.getenv('PERSONAL_DATA_DB_HOST') or "localhost"
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')
    connect = mysql.connector.connect(user=user,
                                      password=password,
                                      host=host,
                                      database=db_name)
    return connect


def main():
    """Fetches user data from the database, format it as log messages,
    and log the redacted messages using the configured logger.
    """
    db = get_db()
    logger = get_logger()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    fields = cursor.column_names
    for row in cursor:
        message = "".join("{}={}; ".format(k, v) for k, v in zip(fields, row))
        logger.info(message.strip())
    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
