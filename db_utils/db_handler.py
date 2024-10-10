import mysql.connector
import os
from mysql.connector import errorcode

def check_and_save_survey(data):
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),      # Replace with your username
            password=os.getenv("DB_PASSWORD"),  # Replace with your password
            database=os.getenv("DB_DATABASE")          # Replace with your database name
        )

        cursor = conn.cursor()

        query = "SELECT COUNT(*) FROM event WHERE event_name = %s AND event_date = %s"
        cursor.execute(query, (data['event_name'], data['event_date']))
        count = cursor.fetchone()[0]

        if count == 0:
            # If it doesn't exist, insert it
            insert_query = """
                        INSERT INTO event (
                            event_name, 
                            event_date, 
                            event_style, 
                            event_location, 
                            event_description, 
                            event_contacts, 
                            event_url, 
                            event_tags,
                            group_name
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
            cursor.execute(insert_query, (
                data['event_name'],
                data['event_date'],
                data['event_style'],
                data['event_location'],
                data['event_description'],
                data['event_contacts'],
                data['event_url'],
                data['event_tags'],
                data['chosen_group']
            ))
            conn.commit()
            print(f"Event '{data['event_name']}' saved successfully with ID {cursor.lastrowid}.")
            return False  # Indicate that the survey text was saved
        else:
            print(f"Event '{data['event_name']}' already exists.")
            return True  # Indicate that the survey text already exists

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    finally:
        cursor.close()
        conn.close()