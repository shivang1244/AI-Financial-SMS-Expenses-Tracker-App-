import mysql.connector


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",        
            port=3306,
            user="sms_user",        
            password="sms1234",     
            database="sms_backend"
        )
        return connection

    except Exception as e:
        print(" MySQL Connection Error:", e)
        return None
