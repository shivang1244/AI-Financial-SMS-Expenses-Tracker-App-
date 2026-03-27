# AI Financial SMS Expenses Tracker App

This project is an AI-based expense tracking system built with two parts:

- Android frontend built in Android Studio
- Python backend built with FastAPI

The app reads SMS messages on the Android side, sends the message text and device location to the backend, and the backend filters financial transaction SMS, extracts useful transaction details, and stores the result.

## Project Overview

The goal of this project is to automatically identify transaction SMS messages and convert them into structured expense records.

Main flow:

1. Android app reads incoming SMS data
2. Android app sends SMS text, latitude, and longitude to the backend
3. Backend checks whether the SMS is a financial transaction
4. Backend extracts amount, bank, direction, payment type, category, and location-based information
5. Backend stores valid transactions in MySQL
6. Android app can fetch saved transactions from the backend

## Frontend

The frontend is an Android application developed in Android Studio.

Frontend responsibilities:

- Read SMS messages from the device
- Capture location if needed
- Send transaction-related data to the backend
- Display saved transactions to the user

Suggested frontend features:

- SMS permission handling
- Internet permission
- Location permission
- Transaction history screen
- Expense summary screen

## Backend

The backend in this repository is built with FastAPI and processes SMS messages received from the Android app.

Backend responsibilities:

- Receive SMS data from Android
- Filter transaction SMS
- Extract structured transaction details
- Reverse geocode coordinates into address details
- Save transactions into MySQL
- Return stored transactions through API endpoints

## Backend Files

- `app.py` - main FastAPI server and API routes
- `predictor.py` - transaction processing and prediction pipeline
- `utils.py` - transaction filtering helpers
- `geo_utils.py` - reverse geocoding logic
- `transaction_repository.py` - MySQL save and fetch logic
- `db.py` - database connection
- `llm_models.py` - LLM request helper
- `requirement.txt` - Python dependencies

## API Endpoints

### `POST /sms`

Receives SMS data from Android.

Example request body:

```json
{
  "sms": "Sent Rs.200 to Rahul via UPI",
  "latitude": 12.9716,
  "longitude": 77.5946
}
```

### `GET /transactions`

Returns saved transactions from MySQL or in-memory fallback storage.

## Tech Stack

### Frontend

- Android Studio
- Java or Kotlin
- HTTP requests to backend API

### Backend

- Python
- FastAPI
- MySQL
- Geopy
- Requests

## How To Run Backend

Install dependencies:

```powershell
pip install -r requirement.txt
```

Run the backend server:

```powershell
uvicorn app:app --reload
```

Backend default local URL:

```txt
http://127.0.0.1:8000
```

## Android To Backend Connection

The Android app should call the backend API with the backend IP address if both devices are on the same network.

Example:

```txt
http://YOUR_LOCAL_IP:8000/sms
```

## GitHub Notes

This repository currently contains the backend project. The Android frontend can be maintained in a separate repository, or both frontend and backend can be documented together if you later add the Android project here.

## Future Improvements

- Improve transaction classification accuracy
- Add better merchant detection rules
- Add charts and expense analytics in Android app
- Secure secrets using environment variables
- Add authentication between frontend and backend

