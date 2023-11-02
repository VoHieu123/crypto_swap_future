from utils import auto_format as fmt
from utils import substring_after, substring_before
from utils import Range
import time, alarm
from utils import Communication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QFrame, QLineEdit
from PyQt6.QtCore import Qt
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
                    if line_edit.text() == "TL" or line_edit.text() == "TR":
                        line_edit.setText("-5.0")
                    elif line_edit.text() == "BL" or line_edit.text() == "BR":
                        line_edit.setText("-10.0")
                    line_edit.returnPressed.connect(line_edit.clearFocus)
                    line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    line_edit.setStyleSheet("""QLineEdit { background: transparent;}""")

    # def on_enter_pressed(self):
    #     line_edit = self.sender()
    #     for coin, types in self.line_edit_dict.items():
    #         for type, positions in types.items():
    #             for position, target_line_edit in positions.items():
    #                 if target_line_edit == line_edit:
    #                     pass

    def update_data(self):
        f = lambda a, b: ((a - b) * 2 / (a + b)) * 100
        def g(coin, type, position):
            try:
                return float(self.line_edit_dict[coin][type][position].text())
            except:
                return -float("inf") if "B" in position else float("inf")

        for coin, symbol in self.bin_coin_symbols.items():
            ask_s, bid_s = self.BinanceHandler_.get_most_recent_bid_ask(symbol[0])
            ask_q, bid_q = self.BinanceHandler_.get_most_recent_bid_ask(symbol[1])
            ask_b, bid_b = self.BinanceHandler_.get_most_recent_bid_ask(symbol[2])
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
                    if value > g(coin, type, "T" + position) or value < g(coin, type, "B" + position):
                        alarm.activate(message=f"Swap-future alarm: {coin}")
                        self.line_edit_dict[coin][type]["M" + position].setStyleSheet("""QLineEdit { background: transparent; background-color: yellow;}""")
                    else:
                        self.line_edit_dict[coin][type]["M" + position].setStyleSheet("""QLineEdit { background: transparent;}""")
                    self.line_edit_dict[coin][type]["M" + position].setText(f"{round(value, 3)}")

        self.update_time = time.time()

    def data_loop(self):
        if int(self.current_time/self.retrieve_frequency) < int(time.time()/self.retrieve_frequency):
            self.update_data()
            # Todo: self.uiMainWindow_.label_infinity.setText(f"Total: {fmt(datetime.datetime.now().strftime('%H:%M:%S'), color='red')}")

        self.current_time = time.time()
        if self.current_time - self.update_time > self.alarm_error_duration:
            alarm.activate("Program can't connect with servers.", alarm=True)
            self.update_time += 15