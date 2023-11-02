from utils import auto_format as fmt
from utils import substring_after, substring_before
from utils import Range
import time, alarm
from utils import Communication
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLineEdit
import datetime
import binance_handler, bybit_handler, okx_handler

class Controller():
    def __init__ (self, uiMainWindow, communication: Communication):
        self.update_time = 0
        self.alarm_error_duration = 60*60
        self.retrieve_frequency = 30
        self.current_time = 0
        self.communication_ = communication
        self.BinanceHandler_ = binance_handler.BinanceHandler()
        self.BybitHandler_ = bybit_handler.BybitHandler()
        self.OKXHandler_ = okx_handler.OKXHandler()
        self.uiMainWindow_ = uiMainWindow

        self.bin_coin_symbols = {}

        self.line_edit_dict = {
            "BTCUSD": {"SQ": {}, "SB": {},"QB": {},},
            "BTCUSDT": {"SQ": {}, "SB": {},"QB": {},},
            "ETHUSD": {"SQ": {}, "SB": {},"QB": {},},
            "ETHUSDT": {"SQ": {}, "SB": {},"QB": {},},
            "ADAUSD": {"SQ": {}, "SB": {},"QB": {},},
            "LINKUSD": {"SQ": {}, "SB": {},"QB": {},},
            "BCHUSD": {"SQ": {}, "SB": {},"QB": {},},
            "DOTUSD": {"SQ": {}, "SB": {},"QB": {},},
            "BNBUSD": {"SQ": {}, "SB": {},"QB": {},},
        }

        for coin in self.line_edit_dict.keys():
            self.bin_coin_symbols[coin] = [f"{coin}{post_fix}" for post_fix in ["_PERP" if "USDT" not in coin else "", "_231229", "_240329"]]

        coin_frame_map = {'a': 'BTCUSD', 'b': 'BTCUSDT', 'c': 'ETHUSD', 'd': 'ETHUSDT', 'e': 'ADAUSD', 'f': 'LINKUSD', 'g': 'BCHUSD', 'h': 'DOTUSD', 'i': 'BNBUSD'}
        type_frame_map = {"1": 'SQ', "2": 'SB', "3": 'QB'}

        frames = self.uiMainWindow_.findChildren(QFrame)
        for frame in frames:
            frame_name = frame.objectName()
            if frame_name[-1] in type_frame_map.keys() and frame_name[-2] in coin_frame_map.keys():
                coin = coin_frame_map[frame_name[-2]]
                type = type_frame_map[frame_name[-1]]
                line_edits = frame.findChildren(QLineEdit)
                for line_edit in line_edits:
                    self.line_edit_dict[coin][type][line_edit.text()] = line_edit

    def update_data(self):
        f = lambda a, b: ((a - b) * 2 / (a + b)) * 100
        for coin, symbol in self.bin_coin_symbols.items():
            ask_s, bid_s = self.BinanceHandler_.get_most_recent_bid_ask(symbol[0])
            ask_q, bid_q = self.BinanceHandler_.get_most_recent_bid_ask(symbol[1])
            ask_b, bid_b = self.BinanceHandler_.get_most_recent_bid_ask(symbol[2])
            self.line_edit_dict[coin]["SQ"]["ML"].setText(f"{round(f(ask_s, bid_q), 2)}")
            self.line_edit_dict[coin]["SQ"]["MR"].setText(f"{round(f(ask_q, bid_s), 2)}")
            self.line_edit_dict[coin]["SB"]["ML"].setText(f"{round(f(ask_s, bid_b), 2)}")
            self.line_edit_dict[coin]["SB"]["MR"].setText(f"{round(f(ask_b, bid_s), 2)}")
            self.line_edit_dict[coin]["QB"]["ML"].setText(f"{round(f(ask_q, bid_b), 2)}")
            self.line_edit_dict[coin]["QB"]["MR"].setText(f"{round(f(ask_b, bid_q), 2)}")

        self.update_time = time.time()

    def data_loop(self):
        if int(self.current_time/self.retrieve_frequency) < int(time.time()/self.retrieve_frequency):
            self.update_data()
            # Todo: self.uiMainWindow_.label_infinity.setText(f"Total: {fmt(datetime.datetime.now().strftime('%H:%M:%S'), color='red')}")

        self.current_time = time.time()
        if self.current_time - self.update_time > self.alarm_error_duration:
            alarm.activate("Program can't connect with servers.", alarm=True)
            self.update_time += 15