import requests
import pandas as pd
import os
from google.cloud import storage

# Configurations
API_KEY = "YOUR_API_KEY_FROM_ALPHA_VANTAGE"
GCS_BUCKET_NAME = "your-data-bucket"
SAVE_PATH_GCS = "your_data/"
LOCAL_SAVE_DIR = "/home/airflow/gcs/data/ingest/temp_raw_data"

CRYPTO_SYMBOLS = ["BTC", "ETH"]
MARKET = "USD"

# Client Initioalization for Google Cloud Storage
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# Check local folder
os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)

def fetch_crypto_data(symbol):
    """Get daily price data from Alpha Vantage."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "DIGITAL_CURRENCY_DAILY",
        "symbol": symbol,
        "market": MARKET,
        "apikey": API_KEY,
    }
    response = requests.get(url, params=params)
    data = response.json()
    time_series = data.get("Time Series (Digital Currency Daily)", {})
    
    if not time_series:
        print(f"⚠️ Failed get data for {symbol}")
        return None
    
    df = pd.DataFrame.from_dict(time_series, orient="index")
    df = df[["1. open", "2. high", "3. low", "4. close", "5. volume"]]
    df.columns = ["open", "high", "low", "close", "volume"]
    df.index = pd.to_datetime(df.index)
    return df

def upload_to_gcs_and_save_local(df, filename):
    """Save CSV file to local and upload to GCS."""
    local_path = os.path.join(LOCAL_SAVE_DIR, filename)
    
    # Save to local
    df.to_csv(local_path, index=True)
    print(f"✅ Data saved in local: {local_path}")
    
    # Upload to GCS (overwrite old file if any)
    blob = bucket.blob(SAVE_PATH_GCS + filename)
    blob.upload_from_filename(local_path)
    print(f"🚀 File {filename} success uploaded to GCS.")

def main():
    for symbol in CRYPTO_SYMBOLS:
        df = fetch_crypto_data(symbol)
        if df is not None:
            filename = f"{symbol.lower()}_{MARKET.lower()}_daily.csv"
            upload_to_gcs_and_save_local(df, filename)

if __name__ == "__main__":
    main()