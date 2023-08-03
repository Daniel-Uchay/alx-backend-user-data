import logging
from mysql.connector import connect, Error
from os import getenv
from typing import List, Tuple

def get_db() -> 'MySQLConnection':
    """ Function to get a connector to the database. """
    try:
        username = getenv('PERSONAL_DATA_DB_USERNAME', 'root')
        password = getenv('PERSONAL_DATA_DB_PASSWORD', '')
        host = getenv('PERSONAL_DATA_DB_HOST', 'localhost')
        db_name = getenv('PERSONAL_DATA_DB_NAME')
        connection = connect(user=username, password=password, host=host, database=db_name)
        return connection
    except Error as e:
        print(f"Error connecting to the database: {e}")
        exit(1)

def main() -> None:
    """ Main function to retrieve data and display in a filtered format. """
    formatter = logging.Formatter('[HOLBERTON] user_data %(levelname)s %(asctime)-15s: %(message)s')

    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    pii_fields = ["name", "email", "phone", "ssn", "password"]
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users;")

        for row in cursor:
            filtered_row = {field: '***' for field in pii_fields}
            filtered_row['ip'] = row['ip']
            filtered_row['last_login'] = row['last_login']
            filtered_row['user_agent'] = row['user_agent']

            log_message = "; ".join([f"{key}={value}" for key, value in filtered_row.items()])
            logger.info(log_message)

    except Error as e:
        print(f"Error fetching data from the database: {e}")
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    main()
