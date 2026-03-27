import re



KNOWN_BANKS = {
    "ICICI": ["ICICI"],
    "HDFC": ["HDFC"],
    "SBI": ["SBI", "STATE BANK OF INDIA"],
    "AXIS": ["AXIS"],
    "KOTAK": ["KOTAK"],
    "YES BANK": ["YES BANK"],
    "IDFC": ["IDFC"],
    "FEDERAL": ["FEDERAL"],
    "PNB": ["PNB", "PUNJAB NATIONAL BANK"],
    "BOB": ["BOB", "BANK OF BARODA"],
    "BANK OF MAHARASHTRA": ["BANK OF MAHARASHTRA"]
}

DEBIT_KEYWORDS = [
    "paid", "spent", "withdrawn", "debited", "sent", "transfer"
]

CREDIT_KEYWORDS = [
    "credited", "received", "refund", "reversed"
]

UPI_KEYWORDS = [
    "upi", "vpa", "@upi", "phonepe", "gpay", "paytm", "bhim"
]

MANDATE_KEYWORDS = [
    "mandate", "autopay", "emi", "auto-debit"
]



def normalize_text(text: str):
    if not text:
        return ""

    return (
        text.lower()
        .replace("\n", " ")
        .replace("-", " ")
        .replace(":", " ")
        .replace("*", "")   
        
    )













def has_account_reference(text):
    if not text:
        return False

    t = normalize_text(text)

    patterns = [
        r'a\/c\s?[xX]?\d{3,}',   
        r'a\/c\s?\*\d{3,}',      
        r'account\s?.*?\d{3,}',  
        r'\bxx\d{3,}\b',
        r'\b\d{4}\b'             
    ]

    return any(re.search(p, t) for p in patterns)



def extract_amount(text: str):
    if not text:
        return None

    t = normalize_text(text)

    match = re.search(
        r'(?:rs|₹|inr)[\s:.]*([\d,]+(?:\.\d{1,2})?)',
        t
    )

    if not match:
        return None

    return float(match.group(1).replace(",", ""))



def extract_direction(text):
    if not text:
        return "UNKNOWN"

    t = normalize_text(text)

    if any(k in t for k in DEBIT_KEYWORDS):
        return "DEBIT"

    if any(k in t for k in CREDIT_KEYWORDS):
        return "CREDIT"

    return "UNKNOWN"



def is_financial_transaction(text: str):
    if not text:
        return False

    amount = extract_amount(text)
    direction = extract_direction(text)
    account_ref = has_account_reference(text)

    
    if amount is None:
        return False

    if direction == "UNKNOWN":
        return False

    if not account_ref:
        return False

    return True