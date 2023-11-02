import uuid
from PyQt6.QtCore import pyqtSignal, QObject
import win32api, datetime
from time import sleep
from binance import Client
from pybit.unified_trading import HTTP
from okx import PublicData
import computer_specific
import alarm

okx_client = PublicData.PublicAPI(debug=False)
bybit_client = HTTP(testnet=False)
binance_client = Client()
clients = {"Binance": binance_client, "Bybit": bybit_client, "OKX": okx_client}

def resynch() -> bool:
    def get_time(client):
        try:
            if client == binance_client:
                server_time = client.get_server_time()["serverTime"]
            elif client == bybit_client:
                server_time = client.get_server_time()["time"]
            elif client == okx_client:
                server_time = client.get_system_time()["data"][0]["ts"]
            return server_time
        except Exception as e:
            alarm.activate(message=f"{e}", to=["Hieu"])
            return None

    for _, client in clients.items():
        epoch_time = get_time(client)
        if epoch_time is not None:
            utcTime = datetime.datetime.utcfromtimestamp(epoch_time // 1000)
            try:
                win32api.SetSystemTime(utcTime.year, utcTime.month, 0, utcTime.day, utcTime.hour, utcTime.minute, utcTime.second, epoch_time % 1000)
            except Exception as e:
                alarm.activate(message=f"{e}", to=["Hieu"])
                break
            return True

    alarm.activate(message="Could not update time", to=["Hieu"])
    return False

class Communication(QObject):
    ui_signal = pyqtSignal()

class Range:
    def __init__(self, start: float, end: float):
        if start > end and start != -1 and end!= -1:
            exit("Range object error.")
        self.start = start
        self.end = end

    def __eq__(self, __value: object) -> bool:
        return self.start == __value.start and self.end == __value.end

    def out_of_range(self, number) -> bool:
        return number < self.start or number > self.end

def change_last_letter(word, new_letter):
        if len(word) < 1:
            return word

        word_list = list(word)
        word_list[-1] = new_letter
        modified_word = ''.join(word_list)

        return modified_word

def substring_after(s, delim):
    return s.partition(delim)[2]

def substring_before(s, delim):
    return s.partition(delim)[0]

def convert_to_float(data):
    if isinstance(data, dict):
        return {key: convert_to_float(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_float(item) for item in data]
    elif isinstance(data, str):
        try:
            return 0 if data == "" else float(data)
        except ValueError:
            return data
    else:
        return data

def generate_uuid():
    return str(uuid.uuid4())

def auto_format(text, color="black", background_color=None, font_weight="normal", font_size=14):
    return f"<span style='font-size: {font_size}pt; background-color: {background_color}; font-weight: {font_weight}; color: {color};'>{text}</span>" if background_color else \
               f"<span style='font-size: {font_size}pt; color: {color}; font-weight: {font_weight};'>{text}</span>"

if computer_specific.COMPUTER_NAME == "Evan":
    while not resynch():
        sleep(1)