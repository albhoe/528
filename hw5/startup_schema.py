import os
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import socket, struct
import sqlalchemy

PROJECT_ID = os.getenv('PROJECT_ID', 'bucsece528')
INSTANCE_CONNECTION_NAME = os.getenv('INSTANCE_CONNECTION_NAME', '')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'cs528-hw5-database')

connector = Connector()

def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

with pool.connect() as db_conn:
  # create ratings table in our sandwiches database
    db_conn.execute(
        sqlalchemy.text(
        """
            CREATE TABLE IF NOT EXISTS requests (
                id             INT AUTO_INCREMENT PRIMARY KEY,
                timestamp      DATETIME,
                country        VARCHAR(64),
                client_ip      VARCHAR(45),
                gender         VARCHAR(16),
                age            INT,
                income         FLOAT,
                is_banned      BOOLEAN,
                time_of_day    TIME,
                requested_file VARCHAR(256)
            )
        """
        )
    )
  

    # commit transaction (SQLAlchemy v2.X.X is commit as you go)
    db_conn.commit()
    db_conn.execute(
        sqlalchemy.text(
            """
            CREATE TABLE IF NOT EXISTS errors (
                id             INT AUTO_INCREMENT PRIMARY KEY,
                timestamp      DATETIME,
                time_of_day    TIME,
                requested_file VARCHAR(256),
                error_code     INT
            )
        """
        )
    )
    db_conn.commit()
connector.close()
print("Schema created successfully.")