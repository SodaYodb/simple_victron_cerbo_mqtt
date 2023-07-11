# Victron Data Logger

This repository contains a Python script that logs data from Victron devices using MQTT and stores it in a PostgreSQL database. It retrieves data such as solar power, grid power, battery information, and more.

## Prerequisites

Before running the script, make sure you have the following prerequisites installed:

- Python (version 3.6 or higher)
- Paho MQTT library (`pip install paho-mqtt`)
- Psycopg2 library (`pip install psycopg2`)

## Configuration

To configure the script, follow these steps:

1. Replace the placeholder values in the code with your specific configuration:
   - `REPLACE_WITH_VICTRON_DEVICE_IP`: Replace with the IP address of your Victron device.
   - `REPLACE_WITH_PG_HOST`: Replace with the hostname or IP address of your PostgreSQL server.
   - `REPLACE_WITH_DB_NAME`: Replace with the name of your PostgreSQL database.
   - `REPLACE_WITH_USERNAME`: Replace with your PostgreSQL username.
   - `REPLACE_WITH_PASSWORD`: Replace with your PostgreSQL password.
   - `REPLACE_WITH_PORT`: Replace with the port number for your PostgreSQL server.

2. Set up the Database:
Table name: `local_vrm_data` or change this in ... def write_postgress(items): ... cur.execute ...

| Column   | Type                | Description                            |
| -------- | ------------------- | -------------------------------------- |
| d_time   | Timestamp with TZ   | Timestamp of the logged data            |
| value_id | Text                | Identifier for the logged value         |
| value    | Numeric             | The value of the logged data            |


Feel free to contribute and make improvements! If you encounter any issues or have any questions, please create an issue in the repository.
