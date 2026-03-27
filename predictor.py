

from datetime import datetime
from zoneinfo import ZoneInfo
import re

from geo_utils import osm_reverse_geocode


from utils import (
    extract_direction,   
    extract_amount,
    has_account_reference,
    is_financial_transaction,
    KNOWN_BANKS,
    DEBIT_KEYWORDS,
    CREDIT_KEYWORDS,
    UPI_KEYWORDS,
    MANDATE_KEYWORDS
)

from llm_models import call_gpt




PAYMENT_TYPES = [
    "P2P",
    "UPI_MERCHANT",
    "CREDIT_CARD",
    "DEBIT_CARD",
    "NEFT",
    "RTGS",
    "CASH_ATM",
    "WALLET",
    "AUTO_DEBIT_EMI",
    "REFUND"
]


# Transaction filtering 

def is_transaction_sms(text: str) -> bool:
    return is_financial_transaction(text)





def gpt_predict(raw_message: str, geo_data: dict):

    prompt = f"""
You are a financial transaction extraction system.

SMS:
"{raw_message}"

Location Address:
"{geo_data.get('address')}"

Merchant:
"{geo_data.get('business_name')}"

Location type:
"{geo_data.get('osm_category')}"

---

Use these keyword guides:
payment types:
{PAYMENT_TYPES}
Banks:
{KNOWN_BANKS}

Debit keywords:
{DEBIT_KEYWORDS}

Credit keywords:
{CREDIT_KEYWORDS}

UPI keywords:
{UPI_KEYWORDS}

Subscription keywords:
{MANDATE_KEYWORDS}

---

Extract the following fields:
0. business_name  
   Determine the REAL merchant/business name.

   Use:
   - SMS content
   - Location address
   - Location type (osm_category)

   --- DECISION LOGIC ---

   - If a clear business/shop/service is mentioned in SMS:
       → return that name

   - Else if location strongly indicates a real place (restaurant, store, fuel station, etc.):
       → extract meaningful name from address ONLY if it looks like a real business

   --- STRICT RULES ---

   - DO NOT return:
       • address fragments (e.g. "10A Main", "3rd Cross", "Block 4")
       • generic names (e.g. "Building", "Road", "Area")
       • partial address text

   - If the extracted value looks like:
       • house number
       • street name
       • numeric/alphanumeric address
       → return "NOT_APPLICABLE"

   - If no clear merchant exists → "NOT_APPLICABLE"
1. bank  
   - Must match known banks from list  
   - Only extract bank if explicitly written in SMS text (e.g., "HDFC Bank", "ICICI Bank")  
   
   STRICTLY DO NOT:
   - Do NOT extract bank from UPI IDs (e.g., rahul@okhdfc, 62@icici, name@ybl)  
   - Do NOT extract bank from VPA handles  
   - Do NOT infer bank from email-like IDs or handles  

   Examples:
   - "from HDFC Bank A/c" → HDFC 
   - "from ICICI Bank account" → ICICI 
   - "sent to rahul@okhdfc" → NOT_APPLICABLE 
   - "credited via VPA 62@icici" → NOT_APPLICABLE 

   If bank is not explicitly written → "NOT_APPLICABLE"
2. transaction_direction  
   - DEBIT or CREDIT  
   - If unclear → "NOT_APPLICABLE"

3. payment_type  
   - One of:
     UPI, UPI_MERCHANT, P2P, CREDIT_CARD, DEBIT_CARD, NEFT, RTGS, CASH_ATM, WALLET, AUTO_DEBIT_EMI, REFUND, NOT_APPLICABLE  

   - You MUST always return this field  

   Mapping logic:

   --- UPI (STRICT) ---
   - If ANY UPI signal is present (e.g. "@", "vpa", "@upi", "@okhdfc", "@ybl", "@okicici", etc.) → ALWAYS return "UPI"
   - Do NOT classify as UPI_MERCHANT or P2P just because a name or handle is present
   - VPA handles (like name@bank) are NOT proof of merchant or person

   --- UPI_MERCHANT (STRICT) ---
   - Only return UPI_MERCHANT if:
       - A CLEAR business/merchant/shop/service name is explicitly mentioned
       - Example: Amazon, Swiggy, Zomato, Reliance, etc.
   - Do NOT assume merchant from UPI ID

   --- P2P (STRICT) ---
   - Only return P2P if:
       - A clear human name is explicitly mentioned in text
       - AND context shows transfer to/from a person
       - Example: "to Rahul", "from Amit Kumar"
   - Do NOT infer person from UPI ID

   --- OTHER RULES ---
   - If mandate/subscription keywords → AUTO_DEBIT_EMI  
   - If ATM keyword → CASH_ATM  
   - If NEFT/RTGS present → NEFT / RTGS  
   - If refund/reversed → REFUND  
   - If card keywords → CREDIT_CARD / DEBIT_CARD  

   - If sms contains "credit alert" or "debit alert":
       - Do NOT classify as CREDIT_CARD/DEBIT_CARD unless explicitly stated

   - If no strong signal → "NOT_APPLICABLE"

4. category  
   You are a strict financial transaction categorization system.

   Use ALL available signals:
   - SMS text
   - merchant name
   - location type (osm_category)

   --- DECISION LOGIC (FOLLOW STEP-BY-STEP) ---

   STEP 1 — Identify transaction nature:
   - If message is bank-related (credit alert, debit alert, account update, transfer, UPI credit/debit without merchant context)
     → category = "Transfer"

   STEP 2 — Use location intelligence (HIGH PRIORITY):
   - If osm_category is available:
       restaurant, cafe → Food  
       supermarket, grocery → Groceries  
       petrol_station → Fuel  
       hospital, pharmacy → Medical  
       mall, retail, shop → Shopping  

   STEP 3 — Use merchant understanding (ONLY if strong signal):
   - If merchant clearly represents a business/service:
       food brands → Food  
       fuel stations → Fuel  
       shopping brands → Shopping  
   - Ignore generic names like:
       "Karuna Trust", "Services", "Solutions", etc.

   STEP 4 — Validate category correctness:
   - Category must represent WHAT money was spent on
   - NOT who processed the transaction
   - NOT bank name
   - NOT random entity name

   --- STRICT RESTRICTIONS ---

   - Do NOT return:
       • bank names (HDFC, ICICI, SBI, etc.)
       • merchant names directly
       • location names directly

   - Do NOT guess from weak signals  
   - Do NOT hallucinate  

   --- FALLBACK ---

   - If no strong evidence → "NOT_APPLICABLE"
   
---


STRICT RULES:
- Do NOT guess
- Do NOT hallucinate
- If unsure → return "NOT_APPLICABLE"
- Output STRICT JSON only
- No explanation

---

Output:
{{
  "business_name": "",
  "bank": "",
  "transaction_direction": "",
  "payment_type": "",
  "category": ""
}}
"""

    messages = [{"role": "user", "content": prompt}]

    output = call_gpt(messages)

    if not output:
        return {"bank": "NOT_APPLICABLE",
                "business_name": "NOT_APPLICABLE",
                "transaction_direction": "NOT_APPLICABLE",
                "payment_type": "NOT_APPLICABLE",
                "category": "NOT_APPLICABLE"
           
        }

    import json
    import re

    try:
        matches = re.findall(r'\{.*?\}', output, re.DOTALL)

        if not matches:
          return {"bank": "NOT_APPLICABLE",
                  "business_name": "NOT_APPLICABLE",
                  "transaction_direction": "NOT_APPLICABLE",
                  "payment_type": "NOT_APPLICABLE",
                  "category": "NOT_APPLICABLE"
             
          }

        cleaned = matches[0]  
        return json.loads(cleaned)

    except:
       print(" GPT PARSE ERROR:", output)
       return {
               "bank": "NOT_APPLICABLE",
               "transaction_direction": "NOT_APPLICABLE",
               "payment_type": "NOT_APPLICABLE",
               "category": "NOT_APPLICABLE"
       }



def process_sms(raw_message: str, latitude: float, longitude: float):

    if not is_transaction_sms(raw_message):
        return {
            "raw_message": raw_message,
            "is_transaction": False,
            "reason": "Not a transaction message"
        }

    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    date = now.date().isoformat()
    time = now.strftime("%H:%M:%S")

    geo_data = osm_reverse_geocode(latitude, longitude)

    
    gpt_data = gpt_predict(raw_message, geo_data)
    business_name = (gpt_data.get("business_name") or "NOT_APPLICABLE").strip()

    if business_name.upper() == "NOT_APPLICABLE":
     business_name = None

    
    payment_type = (gpt_data.get("payment_type") or "NOT_APPLICABLE").upper().strip()
    final_category = (gpt_data.get("category") or "NOT_APPLICABLE").strip()
    bank = (gpt_data.get("bank") or "NOT_APPLICABLE").upper().strip()
    direction = (gpt_data.get("transaction_direction") or "NOT_APPLICABLE").upper().strip()
    if "@" in raw_message.lower() and bank != "NOT_APPLICABLE":
        upi_part = raw_message.lower().split("@")[-1]

  
        if bank.lower() in upi_part:
         bank = "NOT_APPLICABLE"

    
    amount = extract_amount(raw_message)

    confidence = 0.95  

    return {
        "raw_message": raw_message,
        "date": date,
        "time": time,
        "amount": amount,
        "latitude": latitude,
        "longitude": longitude,
        "business_name": business_name,
        "osm_category": geo_data.get("osm_category"),
        "address": geo_data.get("address"),
        "place_id": geo_data.get("place_id"),
        "final_category": final_category,
        "bank": bank,
        "transaction_direction": direction,
        "predicted_payment_type": payment_type,
        "confidence": confidence,
        "is_transaction": True
    }
