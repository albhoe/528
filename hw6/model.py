print("Hello, World!")

import os
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import socket, struct
import sqlalchemy

PROJECT_ID = os.getenv("PROJECT_ID", "bucsece528")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME", "bucsece528:us-east5:alhoe-hw5-mysqlinstance")
DB_USER = os.getenv("DB_USER", "albert")
DB_PASS = os.getenv("DB_PASS", "pres1789")
DB_NAME = os.getenv("DB_NAME", "528hwdatabase")

connector = Connector()

def getconn():
    conn = connector.connect(
      INSTANCE_CONNECTION_NAME,
      "pymysql",
      user=DB_USER,
      password=DB_PASS,
      db=DB_NAME
    )
    print(f"Database connection established successfully: {conn}")
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

with pool.connect() as db_conn:
    results = db_conn.execute(sqlalchemy.text("SELECT * FROM request_logs LIMIT 100")).fetchall()

    # show results
    for row in results:
        print(row)

connector.close()