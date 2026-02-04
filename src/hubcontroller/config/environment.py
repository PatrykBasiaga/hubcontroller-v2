import os
from dotenv import load_dotenv

load_dotenv()


class Environments:
    PLC_CONTROL_IP = os.getenv("PLC_CONTROL_IP")
    PLC_CONTROL_READ = int(os.getenv("PLC_CONTROL_READ"))
    PLC_CONTROL_WRITE = int(os.getenv("PLC_CONTROL_WRITE"))
    PLC_PHOTOS_READ = int(os.getenv("PLC_PHOTOS_READ"))
    PLC_EXEC_READ = int(os.getenv("PLC_EXEC_READ"))

    PLC_ACK_READ_DB = int(os.getenv("PLC_ACK_READ_DB"))

    PLC_LIVEBIT = int(os.getenv("PLC_LIVEBIT"))
    PLC_RESEND_READ = int(os.getenv("PLC_RESEND_READ"))

    HUB_DEVICE_IP = os.getenv("PLC_CONTROL_IP")
    HUB_DEVICE_SERIAL_NUMBER = os.getenv("HUB_DEVICE_SERIAL_NUMBER")
    HUB_NUMBER_OF_UAVS = int(os.getenv("HUB_NUMBER_OF_UAVS"))
    HUB_NUMBER_OF_BATTERY = int(os.getenv("HUB_NUMBER_OF_BATTERY"))

    ACK_TOPIC = os.getenv("SERVER_MQTT_ACK_TOPIC")
    HEARTBEAT_HUB_TOPIC = os.getenv("SERVER_MQTT_HUB_HEARTBEAT_TOPIC")
    CONTROL_TOPIC = os.getenv("SERVER_MQTT_CONTROL_TOPIC")
    APP_TOPIC = os.getenv("SERVER_MQTT_APP_TOPIC")
    PHOTO_HUB_TOPIC = os.getenv("SERVER_MQTT_PHOTO_TOPIC")

    MQTT_PASSWORD = os.getenv("SERVER_MQTT_PASSWORD")
    MQTT_USERNAME = os.getenv("SERVER_MQTT_USERNAME")
    MQTT_SERVER_ADDRESS = os.getenv("SERVER_IP_ADDRESS")
    MQTT_SERVER_PORT = int(os.getenv("SERVER_MQTT_PORT"))
    MQTT_CLIENT_ID = os.getenv("SERVER_MQTT_CLIENT_HUB_ID")
    CSV_PATH_ACK = os.getenv("CSV_PATH_ACK")
    CSV_PATH_CONTROL = os.getenv("CSV_PATH_CONTROL")
    CSV_PATH_EXEC = os.getenv("CSV_PATH_EXEC")
