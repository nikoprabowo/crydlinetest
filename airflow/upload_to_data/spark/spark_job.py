from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import col, to_date, date_format, last
from pyspark.sql.window import Window
from google.cloud import bigquery

# Create Spark session
spark = SparkSession.builder.appName("CryptoTransform") \
    .config("spark.jars", "gs://spark-lib/bigquery/spark-bigquery-latest.jar") \
    .getOrCreate()

# Path to GCS
bucket = "your-data-bucket"
path = f"gs://{bucket}/your_data/"

# Bigquery Config
bq_project = "yourprojectid"
bq_dataset = "your_data"
bq_temp_bucket = "your-data-bucket"

# Read CSV from GCS and add `id` column
def load_data(filename):
    df = spark.read.csv(path + filename, header=True, inferSchema=True)
    df = df.withColumn("date", to_date(df["_c0"], "yyyy-MM-dd"))  # _c0 is date column
    df = df.drop("_c0")
    df = df.withColumn("id", date_format("date", "yyyyMMdd").cast(IntegerType()))
    df = df.dropDuplicates(["id"])
    return df

# Load Data BTC & ETH
btc_price = load_data("btc_usd_daily.csv")
eth_price = load_data("eth_usd_daily.csv")
btc_sma10 = load_data("btc_sma10.csv")
btc_sma100 = load_data("btc_sma100.csv")
btc_rsi = load_data("btc_rsi.csv")
btc_macd = load_data("btc_macd.csv")
eth_sma10 = load_data("eth_sma10.csv")
eth_sma100 = load_data("eth_sma100.csv")
eth_rsi = load_data("eth_rsi.csv")
eth_macd = load_data("eth_macd.csv")

def join_data(price_df, sma10_df, sma100_df, rsi_df, macd_df):
    price_df = price_df.withColumnRenamed("date", "market_date")
    sma10_df = sma10_df.withColumnRenamed("SMA", "SMA10")
    sma100_df = sma100_df.withColumnRenamed("SMA", "SMA100")
    df = price_df.join(sma10_df, "id", "left").withColumnRenamed("date", "date_sma10") \
                 .join(sma100_df, "id", "left").withColumnRenamed("date", "date_sma100") \
                 .join(rsi_df, "id", "left").withColumnRenamed("date", "date_rsi") \
                 .join(macd_df, "id", "left").withColumnRenamed("date", "date_macd")

    window_spec = Window.orderBy("id").rowsBetween(Window.unboundedPreceding, 0)

    for col_name in ["SMA10", "SMA100", "RSI", "MACD", "MACD_Signal", "MACD_Hist"]:
        if col_name in df.columns:
            df = df.withColumn(col_name, last(col(col_name), True).over(window_spec))

    df = df.drop(*[col for col in df.columns if col.startswith("date_")])
    df = df.dropna()
    return df

btc_df = join_data(btc_price, btc_sma10, btc_sma100, btc_rsi, btc_macd)
eth_df = join_data(eth_price, eth_sma10, eth_sma100, eth_rsi, eth_macd)

# Partition optimation
btc_df = btc_df.repartition(2)
eth_df = eth_df.repartition(2)

# BigQuery Process

btc_table = f"{bq_project}.{bq_dataset}.btc_mediumrare"
eth_table = f"{bq_project}.{bq_dataset}.eth_mediumrare"

def write_to_bq_with_merge(df, table_name):
    client = bigquery.Client()
    temp_table = f"{bq_project}.{bq_dataset}.temp_{table_name.split('.')[-1]}"
    
    df.write.format("bigquery") \
        .option("table", temp_table) \
        .option("temporaryGcsBucket", bq_temp_bucket) \
        .mode("overwrite") \
        .save()
    
    merge_query = f"""
    MERGE `{table_name}` AS target
    USING `{temp_table}` AS source
    ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET
            target.close = source.close,
            target.SMA10 = source.SMA10,
            target.SMA100 = source.SMA100,
            target.RSI = source.RSI,
            target.MACD = source.MACD,
            target.MACD_Signal = source.MACD_Signal,
            target.MACD_Hist = source.MACD_Hist
    WHEN NOT MATCHED THEN
        INSERT *;
    """
    
    try:
        client.get_table(table_name)
    except Exception:
        print(f"Tabel {table_name} not found. Create new table...")
        client.query(f"CREATE TABLE `{table_name}` AS SELECT * FROM `{temp_table}`").result()
        return

    client.query(merge_query).result()
    print(f"✅ Data in {table_name} successfull updated!")

# Save to BigQuery using MERGE
write_to_bq_with_merge(btc_df, btc_table)
write_to_bq_with_merge(eth_df, eth_table)

print("✅ Success Transform & Load to BigQuery!")
spark.stop()