from db import get_connection
import uuid
from datetime import timedelta


# ========================= SAVE TRANSACTION =========================

def save_transaction(data: dict):

    try:
        connection = get_connection()
        cursor = connection.cursor()

        
        transaction_id = str(uuid.uuid4())

        print(" Saving Transaction To MySQL...")
        print("Incoming Data:", data)

        query = """
            INSERT INTO transactions (
                id,
                raw_message,
                amount,
                date,
                time,
                latitude,
                longitude,
                business_name,
                address,
                place_id,
                final_category,
                bank,
                transaction_direction,
                predicted_payment_type,
                confidence
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            transaction_id,
            data.get("raw_message"),
            int(data.get("amount") or 0),
            data.get("date"),
            data.get("time"),
            data.get("latitude"),
            data.get("longitude"),
            data.get("business_name") or None,
            data.get("address") or None,
            data.get("place_id"),
            data.get("final_category") or None,
            data.get("bank") or None,
            data.get("transaction_direction"),
            data.get("predicted_payment_type"),
            data.get("confidence"),
        )

        cursor.execute(query, values)
        connection.commit()

        print(" INSERT SUCCESS")
        print("Inserted ID:", transaction_id)

    except Exception as e:
        print(" ERROR SAVING TO MYSQL:", e)

    finally:
        cursor.close()
        connection.close()



def get_all_transactions():

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM transactions ORDER BY created_at DESC"
        cursor.execute(query)

        results = cursor.fetchall()

        for row in results:

            time_value = row.get("time")

            if isinstance(time_value, timedelta):
                total_seconds = int(time_value.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                row["time"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            elif isinstance(time_value, (int, float)):
                total_seconds = int(time_value)
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                row["time"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            elif time_value is not None:
                row["time"] = str(time_value)

        print(f"Returning {len(results)} transactions from DB")

        return results

    except Exception as e:
        print(" ERROR FETCHING FROM MYSQL:", e)
        return []

    finally:
        cursor.close()
        connection.close()
