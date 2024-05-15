import psycopg2

params = {
    "host": "localhost",
    "port": 5432,
    "dbname": "test",
    "user": "postgres",
    "password": "12345",
    # "sslmode": "verify-ca",
    "sslcert": "/etc/ssl/server.crt",
    "sslkey": "/etc/ssl/server.key"
}

conn = psycopg2.connect(**params)

cur = conn.cursor()

cur.execute("SELECT version()")
version = cur.fetchone()
print(f"Postgres version: {version}")

cur.execute("SELECT * FROM User_Table")
# cur.execute("""INSERT INTO User_Table (UserID, UserName, Password, Usertype) VALUES (%s, %s, %s, %s);""",
# (623422, "Mr Student3", "123453", 'Teacher'))
books = cur.fetchall()
print(f"users: {books}")

# conn.commit()

cur.close()
conn.close()