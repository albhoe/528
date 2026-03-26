import pymysql

connection = pymysql.connect(
    host='35.226.17.220',
    user='root',
    password='',
    database='alhoe-hw5-mysqlinstance'
)

with connection.cursor() as cursor:
    cursor.execute("""
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
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            timestamp      DATETIME,
            time_of_day    TIME,
            requested_file VARCHAR(256),
            error_code     INT
        )
    """)
connection.commit()
connection.close()
print("Schema created successfully.")