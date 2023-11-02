from binance import Client
import time, const, utils
import pandas as pd

class BinanceHandler:
    def __init__(self):
        self.binance_client = Client()

    def get_most_recent_bid_ask(self, input_symbol_array):
        data = pd.DataFrame()

        for input_symbol in input_symbol_array:
            if "USDT" in input_symbol:
                temp = self.binance_client.futures_orderbook_ticker(symbol=input_symbol)
                temp = pd.DataFrame([temp])
            elif "USD" in input_symbol:
                temp = self.binance_client.futures_coin_orderbook_ticker(symbol=input_symbol)
                temp = pd.DataFrame(temp)

            if len(temp) != 0:
                temp = temp[["askPrice", "bidPrice"]]
                temp.rename(columns = {"bidPrice" : "bid_" + input_symbol}, inplace = True)
                temp.rename(columns = {"askPrice" : "ask_" + input_symbol}, inplace = True)
                data = temp if data.empty else data.join(temp)
            else:
                print("No response from symbol: ", input_symbol)
                data[input_symbol] = ''

        return data

    @staticmethod
    def send_http_request(func, **kwargs):
        retries_count = -1
        while True:
            retries_count += 1
            try:
                return utils.convert_to_float(func(**kwargs))
            except Exception as error:
                utils.resynch()
                if retries_count < const.MAX_RETRIES:
                    time.sleep(const.SLEEP_TIME)
                else:
                    raise Exception(f"Error: {error}.")
