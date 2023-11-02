from utils import auto_format as fmt
from utils import substring_after, substring_before
from utils import Range
import time, alarm
from utils import Communication
from PyQt6.QtGui import QFont
import datetime
import binance_handler, bybit_handler, okx_handler

class Controller():
    def __init__ (self, uiMainWindow, communication: Communication):
        self.line_edit_dict = {}
        self.update_time = 0
        self.alarm_error_duration = 60*60
        self.retrieve_frequency = 30
        self.current_time = 0
        self.communication_ = communication
        self.BinanceHandler_ = binance_handler.BinanceHandler()
        self.BybitHandler_ = bybit_handler.BybitHandler()
        self.OKXHandler_ = okx_handler.OKXHandler()
        self.uiMainWindow_ = uiMainWindow

        markets = ["Bi", "Ok", "By"]
        subaccounts = ["M", "1"]

        for market in markets:
            for subaccount in subaccounts:
                label_key = f"{market}{subaccount}U"
                label_name = f"label_{market}{subaccount}U"
                try:
                    ui_label = getattr(self.uiMainWindow_, label_name)
                    self.labelDict[label_key] = ui_label
                except Exception as e:
                    pass

    def diff_in_percentage(input_a: float, input_b: float):
        return (100 * (input_a - input_b)*2/(input_a + input_b))

    def update_data(self):
        self.update_time = time.time()

    def upload_data(self):
        pass
        # bin_coin_symbols = ["ETHUSD_PERP", "ETHUSD_230929", "ETHUSD_231229",
        #                     "BTCUSD_PERP", "BTCUSD_230929", "BTCUSD_231229",]
        #                     # "ETHUSDT", "ETHUSDT_230929", "ETHUSDT_231229",
        #                     # "BTCUSDT", "BTCUSDT_230929", "BTCUSDT_231229"]

        # bin_data = binance_funcs.get_prices(bin_coin_symbols)

        # swap = float(bin_data["ETHUSD_PERP"][0])
        # qtly = float(bin_data["ETHUSD_230929"][0])
        # bi_qtly = float(bin_data["ETHUSD_231229"][0])

        # # notify(swap, qtly, bi_qtly, "BIN", "ETH")

        # swap = float(bin_data["BTCUSD_PERP"][0])
        # qtly = float(bin_data["BTCUSD_230929"][0])
        # bi_qtly = float(bin_data["BTCUSD_231229"][0])

        # notify(swap, qtly, bi_qtly, "BIN", "BTC")

        # okx_coin_symbols = ["ETH-USD-SWAP", "ETH-USD-230929", "ETH-USD-231229",
        #                     "BTC-USD-SWAP", "BTC-USD-230929", "BTC-USD-231229",]
        #                     # "ETH-USDT-SWAP", "ETH-USDT-230929", "ETH-USDT-231229",
        #                     # "BTC-USDT-SWAP", "BTC-USDT-230929", "BTC-USDT-231229"]

        # okx_data = okx_funcs.get_prices(okx_coin_symbols)

        # swap = float(okx_data["ETH-USD-SWAP"][0])
        # qtly = float(okx_data["ETH-USD-230929"][0])
        # bi_qtly = float(okx_data["ETH-USD-231229"][0])

        # # notify(swap, qtly, bi_qtly, "OKX", "ETH")

        # swap = float(okx_data["BTC-USD-SWAP"][0])
        # qtly = float(okx_data["BTC-USD-230929"][0])
        # bi_qtly = float(okx_data["BTC-USD-231229"][0])

        # notify(swap, qtly, bi_qtly, "OKX", "BTC")

        # print("\n")

        # time.sleep(const.NOTIFY_RATE_S)

    def data_loop(self):
        if int(self.current_time/self.retrieve_frequency) < int(time.time()/self.retrieve_frequency):
            self.update_data()
            self.communication_.ui_signal.emit()

        self.current_time = time.time()
        if self.current_time - self.update_time > self.alarm_error_duration:
            alarm.activate("Program can't connect with servers.", alarm=True)
            self.update_time += 15

    def ui_update(self):
        self.upload_data()
        # Todo: self.uiMainWindow_.label_infinity.setText(f"Total: {fmt(datetime.datetime.now().strftime('%H:%M:%S'), color='red')}")