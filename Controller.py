import computer_specific, pickle
from utils import substring_after
import time, alarm, os
from utils import Communication
from PyQt6.QtWidgets import QFrame, QLineEdit, QTabWidget, QApplication
from PyQt6.QtCore import Qt
import binance_handler, bybit_handler, okx_handler
from copy import deepcopy

class Controller():
    def __init__ (self, uiMainWindow, communication: Communication, app: QApplication):
        self.app = app
        self.update_time = 0
        self.alarm_error_duration = 60*60
        self.retrieve_frequency = 30*2
        self.current_time = 0
        self.communication_ = communication
        self.handlers = {
            "Binance": binance_handler.BinanceHandler(),
            "OKX": okx_handler.OKXHandler(),
            "Bybit": bybit_handler.BybitHandler(),
        }
        self.uiMainWindow_ = uiMainWindow

        self.coin_symbols = {
            "Binance": {},
            "OKX": {},
            "Bybit": {},
        }

        binance_keys = 'abcdefghi'
        binance_coins = ["BTCUSD", "BTCUSDT", "ETHUSD", "ETHUSDT",
                         "ADAUSD", "LINKUSD", "BCHUSD", "DOTUSD", "BNBUSD"]
        okx_keys = 'abcdefghijklmn'
        okx_coins = ['BTC-USD', 'BTC-USDT', 'BTC-USDC',
                     'ETH-USD', 'ETH-USDT', 'ETH-USDC',
                     'LTC-USD', 'LTC-USDT', 'XRP-USD', 'XRP-USDT',
                     'EOS-USD', 'EOS-USDT', 'ETC-USD', 'ETC-USDT',]
        bybit_keys = "ab"
        bybit_coins = ["BTC", "ETH"]

        line_edit_template = {"SQ": {}, "SB": {},"QB": {}}
        self.line_edit_dict = {
            "Binance": {coin: deepcopy(line_edit_template) for coin in binance_coins},
            "OKX": {coin: deepcopy(line_edit_template) for coin in okx_coins},
            "Bybit": {coin: deepcopy(line_edit_template) for coin in bybit_coins},
        }
        if os.path.exists(computer_specific.SETTINGS_PATH):
            with open(computer_specific.SETTINGS_PATH, 'rb') as f:
                self.data_model_dict = pickle.load(f)
        else:
            self.data_model_dict = deepcopy(self.line_edit_dict)
        for exchange, line_edit_dict in self.line_edit_dict.items():
            for coin in line_edit_dict.keys():
                if exchange == "Binance":
                    self.coin_symbols[exchange].update({coin: None})
                    self.coin_symbols[exchange][coin] = [f"{coin}{post_fix}" for post_fix in ["_PERP" if "USDT" not in coin else "", "_231229", "_240329"]]
                elif exchange == "OKX":
                    self.coin_symbols[exchange].update({coin: None})
                    self.coin_symbols[exchange][coin] = [f"{coin}{post_fix}" for post_fix in ["-SWAP", "-231229", "-240329"]]
                else:
                    self.coin_symbols[exchange].update({coin: None})
                    self.coin_symbols[exchange][coin] = [f"{coin}{post_fix}" for post_fix in ["PERP", "-29DEC23", "-29MAR24"]]

        tab_widget = None
        tab_widgets = self.uiMainWindow_.findChildren(QTabWidget)
        for tab in tab_widgets:
            if tab.objectName() == "tabWidget_main":
                tab_widget = tab
                break

        tab_dict = {}
        for tab_index in range(tab_widget.count()):
            tab_name = tab_widget.tabText(tab_index)
            tab = tab_widget.widget(tab_index)
            tab_dict[tab_name] = tab

        self.frame_map = {
            "Binance": {"coin_frame_map": {key: coin for key, coin in zip(binance_keys, binance_coins)},
                        "type_frame_map": {"1": 'SQ', "2": 'SB', "3": 'QB'}},
            "OKX": {"coin_frame_map": {key: coin for key, coin in zip(okx_keys, okx_coins)},
                        "type_frame_map": {"1_2": 'SQ', "2_2": 'SB', "3_2": 'QB'}},
            "Bybit": {"coin_frame_map": {key: coin for key, coin in zip(bybit_keys, bybit_coins)},
                      "type_frame_map": {"1_3": 'SQ', "2_3": 'SB', "3_3": 'QB'}}
        }

        for exchange, tab in tab_dict.items():
            type_frame_map = self.frame_map[exchange]["type_frame_map"]
            coin_frame_map = self.frame_map[exchange]["coin_frame_map"]
            frames = tab.findChildren(QFrame)
            for frame in frames:
                frame_name = substring_after(frame.objectName(), "_")
                if frame_name != "" and not frame_name.isdecimal() \
                    and frame_name[0] in coin_frame_map.keys() \
                        and "mainAccount" not in frame_name:
                    coin = coin_frame_map[frame_name[0]]
                    type = type_frame_map[frame_name[1:]]
                    line_edits = frame.findChildren(QLineEdit)
                    for line_edit in line_edits:
                        self.line_edit_dict[exchange][coin][type][line_edit.text()] = line_edit
                        if line_edit.text() in self.data_model_dict[exchange][coin][type]:
                            line_edit.setText(f"{round(float(self.data_model_dict[exchange][coin][type][line_edit.text()]), 3)}")
                        else:
                            if "T" in line_edit.text():
                                line_edit.setText("10.0")
                                self.data_model_dict[exchange][coin][type][line_edit.text()] = 10.0
                            elif "B" in line_edit.text():
                                self.data_model_dict[exchange][coin][type][line_edit.text()] = -10.0
                                line_edit.setText("-10.0")
                        line_edit.returnPressed.connect(lambda: self.on_enter_pressed(self))
                        line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        line_edit.setStyleSheet("""QLineEdit { background: transparent;}""")
        with open(computer_specific.SETTINGS_PATH, "wb") as pkl_file:
            pickle.dump(self.data_model_dict, pkl_file)

    @staticmethod
    def on_enter_pressed(self):
        sender = self.app.sender()
        if isinstance(sender, QLineEdit):
            line_edit = sender
        else:
            return

        line_edit.clearFocus()
        for exchange, coins in self.line_edit_dict.items():
            for coin, types in coins.items():
                for type, positions in types.items():
                    for position, target_line_edit in positions.items():
                        if target_line_edit == line_edit:
                            self.data_model_dict[exchange][coin][type][position] = line_edit.text()
                            with open(computer_specific.SETTINGS_PATH, "wb") as pkl_file:
                                pickle.dump(self.data_model_dict, pkl_file)

    def update_data(self):
        f = lambda a, b: ((a - b) * 2 / (a + b)) * 100

        for exchange, coin_symbols in self.coin_symbols.items():
            for coin, symbol in coin_symbols.items():
                ask_s, bid_s = self.handlers[exchange].get_most_recent_bid_ask(symbol[0])
                ask_q, bid_q = self.handlers[exchange].get_most_recent_bid_ask(symbol[1])
                ask_b, bid_b = self.handlers[exchange].get_most_recent_bid_ask(symbol[2])
                sq_ml = f(ask_s, bid_q)
                sq_mr = f(ask_q, bid_s)
                sb_ml = f(ask_s, bid_b)
                sb_mr = f(ask_b, bid_s)
                qb_ml = f(ask_q, bid_b)
                qb_mr = f(ask_b, bid_q)
                for name, value in locals().items():
                    if "ask" not in name and "bid" not in name \
                        and isinstance(value, float) and name != "value":
                        type = name[:2].upper()
                        position = name[-1].upper()
                        self.data_model_dict[exchange][coin][type]["M" + position] = value

        self.update_time = time.time()

    def data_loop(self):
        if int(self.current_time/self.retrieve_frequency) < int(time.time()/self.retrieve_frequency):
            self.update_data()
            self.communication_.ui_signal.emit()

        self.current_time = time.time()
        if self.current_time - self.update_time > self.alarm_error_duration:
            alarm.activate("Program can't connect with servers.", alarm=True)
            self.update_time += 15

    def upload_data(self):

        def g(exchange, coin, type, position):
            try:
                return float(self.line_edit_dict[exchange][coin][type][position].text())
            except:
                return -float("inf") if "B" in position else float("inf")

        for exchange, coins in self.line_edit_dict.items():
            for coin, types in coins.items():
                for type, positions in types.items():
                    for position in positions.keys():
                        if "M" in position:
                            value = self.data_model_dict[exchange][coin][type][position]
                            if value > g(exchange, coin, type, "T" + position[1]) or value < g(exchange, coin, type, "B" + position[1]):
                                alarm.activate(message=f"Swap-future alarm: {coin}", alarm=True)
                                self.line_edit_dict[exchange][coin][type][position].setStyleSheet("""QLineEdit { background: transparent; background-color: yellow;}""")
                            else:
                                self.line_edit_dict[exchange][coin][type][position].setStyleSheet("""QLineEdit { background: transparent;}""")
                            self.line_edit_dict[exchange][coin][type][position].setText(f"{round(value, 3)}")

    def ui_loop(self):
        self.upload_data()
