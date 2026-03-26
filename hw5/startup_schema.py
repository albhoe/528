import pymysql

connection = pymysql.connect(
    host='YOUR_CLOUD_SQL_IP',
    user='YOUR_USER',
    password='YOUR_PASSWORD',
    database='YOUR_DB'
)

with connection.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            country        VARCHAR(64),
            client_ip      VARCHAR(45),
            gender         VARCHAR(16),
            age            INT,
            income         FLOAT,
            is_banned      BOOLEAN,
            time_of_day    TIMESTAMP,
            requested_file VARCHAR(256)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            time_of_day    TIMESTAMP,
            requested_file VARCHAR(256),
            error_code     INT
        )
    """)
connection.commit()
connection.close()
print("Schema created successfully.")