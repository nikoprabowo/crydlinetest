import requests
import pandas as pd
import os
import time
from google.cloud import storage

# ====== CONFIG ======
BUCKET_NAME = "your-data-bucket"
DESTINATION_FOLDER = "your_data"
LOCAL_DIR = "your_path_VMs/ingest/temp_raw_data"
API_KEY = "YOUR_API_KEY_FROM_ALPHA_VANTAGE"

URL = "https://www.alphavantage.co/query"
SYMBOLS = ["BTC", "ETH"]
INTERVAL = "daily"
SERIES_TYPE = "open"
MAX_RETRIES = 3
SLEEP_BETWEEN_REQUESTS = 20
SLEEP_IF_LIMITED = 60
# =====================

# Remove older CSV files in local folder
def clear_old_csv_files():
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    for file in os.listdir(LOCAL_DIR):
        if file.endswith(".csv"):
            try:
                os.remove(os.path.join(LOCAL_DIR, file))
                print(f"🗑️ Removed local file: {file}")
            except Exception as e:
                print(f"⚠️ Failed remove {file}: {e}")

# Upload files to Google Cloud Storage
def upload_to_gcs(local_file, bucket_name, destination_blob_name):
    if not os.path.exists(local_file) or os.path.getsize(local_file) == 0:
        print(f"⚠️ File {local_file} emty or not found, can't upload.")
        return

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(local_file)
    print(f"✅ Uploaded {local_file} to gs://{bucket_name}/{destination_blob_name}")

# Get indicator data from Alpha Vantage
def fetch_indicator(symbol, function, columns, output_filename, extra_params=None):
    params = {
        "function": function,
        "symbol": symbol,
        "interval": INTERVAL,
        "series_type": SERIES_TYPE,
        "apikey": API_KEY
    }

    if extra_params:
        params.update(extra_params)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(URL, params=params)
            data = response.json()

            if "Information" in data:
                print(f"⏳ Attempt {attempt}: API limit reached. Waiting {SLEEP_IF_LIMITED} seconds...")
                time.sleep(SLEEP_IF_LIMITED)
                continue

            key = f"Technical Analysis: {function}" if function != "MACDEXT" else "Technical Analysis: MACDEXT"
            technical_data = data.get(key, {})

            if not technical_data:
                print(f"⚠️ No data returned for {function} on {symbol}")
                return pd.DataFrame()

            df = pd.DataFrame.from_dict(technical_data, orient="index")
            df = df[columns] if all(col in df.columns for col in columns) else df

            df.to_csv(output_filename)
            print(f"✅ Data saved locally: {output_filename}")
            return df

        except Exception as e:
            print(f"❌ Error fetching {symbol} {function}: {e}")
            time.sleep(SLEEP_IF_LIMITED)

    print(f"❌ Failed get data for {symbol} {function} after {MAX_RETRIES} times try.")
    return pd.DataFrame()


# ====== MAIN SCRIPT ======
print("🔄 Remove local file CSV...")
clear_old_csv_files()

# 🚫 No need remove older files in GCS

# Loop all symbol and indicator
for symbol in SYMBOLS:
    indicators = [
        ("SMA", ["SMA"], f"{symbol.lower()}_sma10.csv", {"time_period": "10"}),
        ("SMA", ["SMA"], f"{symbol.lower()}_sma100.csv", {"time_period": "100"}),
        ("RSI", ["RSI"], f"{symbol.lower()}_rsi.csv", {"time_period": "10"}),
        ("MACDEXT", ["MACD", "MACD_Signal", "MACD_Hist"], f"{symbol.lower()}_macd.csv", None),
    ]

    for function, columns, filename, extra_params in indicators:
        print(f"⏱️ Waiting {SLEEP_BETWEEN_REQUESTS} seconds before next request...")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

        local_file_path = os.path.join(LOCAL_DIR, filename)
        df = fetch_indicator(symbol, function, columns, local_file_path, extra_params)
        upload_to_gcs(local_file_path, BUCKET_NAME, f"{DESTINATION_FOLDER}/{filename}")
        print(f"🔹 Processed {symbol} {function} {extra_params if extra_params else ''}")

print("✅ All data success ingested, saved, and upload!")