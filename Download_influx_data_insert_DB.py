'''
    Connect influx DB
    Using asset id and default series
    Download the time series using start date and end date
    stored it in DB
'''

from influxdb import InfluxDBClient
import csv
import os
import pandas as pd
from DB_Connection import get_db_connection
from dotenv import load_dotenv
import numpy as np

load_dotenv()

table_name = os.getenv("TABLE_NAME")

# #--------------------------------------------------------------------
# Create directory if it doesn't exist
# dir_name = "ts data"
# os.makedirs(dir_name, exist_ok=True)
# #--------------------------------------------------------------------

influx_client = InfluxDBClient(host='172.21.158.16', port=8086, database='cs_iot')

# Query data from InfluxDB for a given month
start_str = '2026-01-06T00:00:00Z'
end_str   = '2026-01-10T23:59:59Z'

query = f"""
SELECT * FROM "AS-000014-7027-default"
WHERE time >= '{start_str}' AND time <= '{end_str}'
"""

result = influx_client.query(query)
points = list(result.get_points())
print(len(points))

df = pd.DataFrame(points)

# print(df.dtypes)
# print(df.columns.tolist())

# ------------------ Fix Data Types ------------------ #

# ------------------ Fix Data Types ------------------ #

# Convert time column
df['time'] = pd.to_datetime(df['time'], format='ISO8601')


# FORCE numeric conversion (THIS IS THE KEY FIX)
for col in df.columns:
    if col != 'time':
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Convert NaN → None (for SQL NULL)
df = df.where(pd.notnull(df), None)


#--------------------------------------------------------------------
# following code is used to save downloaded data in to .csv file
#--------------------------------------------------------------------
# # Find next file number
# existing_files = [f for f in os.listdir(dir_name) if f.startswith("influx_data_") and f.endswith(".csv")]
#
# file_numbers = []
# for f in existing_files:
#     try:
#         num = int(f.replace("influx_data_", "").replace(".csv", ""))
#         file_numbers.append(num)
#     except:
#         pass
#
# next_number = max(file_numbers) + 1 if file_numbers else 1
#
# file_path = os.path.join(dir_name, f"influx_data_{next_number}.csv")
#
# # Save CSV
# if points:
#     headers = points[0].keys()
#
#     with open(file_path, mode='w', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=headers)
#         writer.writeheader()
#         writer.writerows(points)
#
#     print(f"CSV saved as: {file_path}")
# else:
#     print("No data to save")
#--------------------------------------------------------------------

for col in df.columns:
    if col != 'time':
        try:
            max_val = df[col].max()
            min_val = df[col].min()
            print(f"{col} → min: {min_val}, max: {max_val}")
        except:
            pass



        # Replace invalid SQL values
        df = df.replace([np.inf, -np.inf], None)

        # Convert NaN → None (SQL NULL)
        df = df.where(pd.notnull(df), None)

# ------------------ DB Connection ------------------ #
conn = get_db_connection()
cursor = conn.cursor()

cursor.fast_executemany = True

# ------------------ Insert ------------------ #
columns = list(df.columns)
col_str = ", ".join(columns)
placeholders = ", ".join(["?"] * len(columns))

insert_query = f"""
INSERT INTO {table_name} ({col_str})
VALUES ({placeholders})
"""

data = [tuple(row) for row in df.to_numpy()]

cursor.executemany(insert_query, data)

conn.commit()
cursor.close()
conn.close()

print(f"Data inserted into table: {table_name}")