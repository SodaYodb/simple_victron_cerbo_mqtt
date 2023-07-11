import paho.mqtt.client as mqtt
import json
import time
import psycopg2
import threading

from datetime import datetime, timedelta


vrm_address = "REPLACE_WITH_VICTRON_DEVICE_IP"

pghost = "REPLACE_WITH_PG_HOST"
pgdbname = "REPLACE_WITH_DB_NAME"
pguser = "REPLACE_WITH_USERNAME"
pgpassword = "REPLACE_WITH_PASSWORD"
pgport = "REPLACE_WITH_PORT"

write_duration = 10 #modify if you want/need a longer duration to collect values

victron_id = None
buffered_values = {}


def on_first_message(client, userdata, msg):
    global victron_id
    json_payload = json.loads(msg.payload.decode('utf-8'))
    if "system/0/Serial" in str(msg.topic):
        victron_id = (str(json_payload["value"]))


client = mqtt.Client()
client.on_message = on_first_message
client.connect(vrm_address, 1883, 60)
client.loop_start()
client.subscribe("#")
time.sleep(2)
client.loop_stop()

print(f' your Victron ID is: {victron_id}')


def write_postgress(items):
    pgconncet = psycopg2.connect(
        host = pghost,
        dbname = pgdbname,
        user = pguser,
        password = pgpassword,
        port = pgport
    )
    pgconncet.autocommit = True
    cur = pgconncet.cursor()
    cur.execute("INSERT INTO local_vrm_data (d_time, value_id, value) VALUES (%s, %s, %s)", (items[0], items[1], items[2]))
    cur.close()
    pgconncet.close()


def on_connect(client, userdata, flags, rc):
    client.publish(f'R/{victron_id}/keepalive')
    # solar data
    client.subscribe(f'N/{victron_id}/system/0/Dc/Pv/Power')
    # grid data
    client.subscribe(f'N/{victron_id}/grid/31/Ac/L1/Power')
    client.subscribe(f'N/{victron_id}/grid/31/Ac/L2/Power')
    client.subscribe(f'N/{victron_id}/grid/31/Ac/L3/Power')
    client.subscribe(f'N/{victron_id}/vebus/276/Ac/Out/L1/V')
    # Batteries data
    client.subscribe(f'N/{victron_id}/system/0/Batteries')
    

def on_message(client, userdata, msg):
    excluded_keys = ["instance", "name", "id", "state", "active_battery_service"]
    try:
        json_payload = json.loads(msg.payload.decode('utf-8'))
        value_id = ""
        if json_payload["value"] != None:
            if str(msg.topic) == f'N/{victron_id}/system/0/Dc/Pv/Power':
                value_id = "Solar"
            elif str(msg.topic) == f'N/{victron_id}/grid/31/Ac/L1/Power':
                value_id = "L1"
            elif str(msg.topic) == f'N/{victron_id}/grid/31/Ac/L2/Power':
                value_id = "L2"
            elif str(msg.topic) == f'N/{victron_id}/grid/31/Ac/L3/Power':
                value_id = "L3"
            elif str(msg.topic) == f'N/{victron_id}/vebus/276/Ac/Out/L1/V':
                value_id = "L1_Volt"
            elif str(msg.topic) == f'N/{victron_id}/system/0/Batteries':
                for key , value in json_payload["value"][0].items():
                    if key not in excluded_keys:
                        b_value_id = "b_" + str(key)
                        add_to_buffer(b_value_id, value)
            if value_id:
                add_to_buffer(value_id, json_payload["value"])
    except json.JSONDecodeError:
            print(f"failed decode msg: {msg.payload}")

def add_to_buffer(value_id, value):
    if value_id not in buffered_values:
        buffered_values[value_id] = []
    buffered_values[value_id].append(value)

    
def process_buffer():
    for value_id, values in buffered_values.items():
        if values:
            write_time = datetime.now()
            mean_value = sum(values) / len(values)
            write_postgress([write_time, value_id, mean_value])
            buffered_values[value_id] = []
    threading.Timer(write_duration, process_buffer).start()


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Disconnected. Trying to reconnect...")
        client.reconnect()


def keep_alive():
    #print("keep alive", datetime.now.strftime("%H:%M:%S"))
    work_client.publish(f'R/{victron_id}/keepalive', '')
    threading.Timer(keep_alive_duration, keep_alive).start()


work_client = mqtt.Client()
work_client.on_connect = on_connect
work_client.on_message = on_message
work_client.on_disconnect = on_disconnect

work_client.connect(vrm_address, 1883, 60)

process_buffer()
keep_alive()
work_client.loop_forever()
