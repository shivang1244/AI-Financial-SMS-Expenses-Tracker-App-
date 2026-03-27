## In this file - creating a web server runs on local machine using the FastAPI framework. It define two API endpoints
# importing bases model so we can shape the data we expect to recive in an API request 
#  
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from predictor import process_sms
from datetime import datetime
import json


from transaction_repository import save_transaction, get_all_transactions

app = FastAPI()


TRANSACTIONS: List[dict] = []


class SMSRequest(BaseModel):
    sms: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None



@app.post("/sms")
def receive_sms(data: SMSRequest):

    print("\n DATA RECEIVED FROM ANDROID")
    print("SMS TEXT :", data.sms)
    print("LATITUDE :", data.latitude)
    print("LONGITUDE:", data.longitude)
    print("-" * 60)

    result = process_sms(
        data.sms,
        data.latitude,
        data.longitude
    )

    
    if result.get("is_transaction"):

        now = datetime.now()
        result.setdefault("date", now.date().isoformat())
        result.setdefault("time", now.time().strftime("%H:%M:%S"))

        
        TRANSACTIONS.insert(0, result)

        
        try:
            save_transaction(result)
            print(" Saved to MySQL")
        except Exception as e:
            print(" DB Save Error:", e)

    print("FINAL PIPELINE OUTPUT")
    print(json.dumps(result, indent=2))
    print("=" * 60)

    return result




@app.get("/transactions")
def get_transactions():

    try:
        db_transactions = get_all_transactions()

        if db_transactions:

            print(" Returning transactions from DB")

            serialized = []

            for txn in db_transactions:

                
                date_value = txn.get("date")
                if hasattr(date_value, "isoformat"):
                    date_value = date_value.isoformat()

                
                time_value = txn.get("time")
                if hasattr(time_value, "strftime"):
                    time_value = time_value.strftime("%H:%M:%S")

                serialized.append({
                    **txn,
                    "date": date_value,
                    "time": time_value
                })

            return serialized

    except Exception as e:
        print("DB Fetch Error:", e)

    print(" Returning transactions from memory")
    return TRANSACTIONS
