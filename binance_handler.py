from binance import Client
import time, const, utils

class BinanceHandler:
    def __init__(self):
        self.binance_client = Client()

    def get_most_recent_bid_ask(self, input_symbol):
        if "USDT" in input_symbol:
            data = self.send_http_request(self.binance_client.futures_orderbook_ticker, symbol=input_symbol)
            ask, bid = data["askPrice"], data["bidPrice"]
        elif "USD" in input_symbol:
            data = self.send_http_request(self.binance_client.futures_coin_orderbook_ticker, symbol=input_symbol)
            ask, bid = data[0]["askPrice"], data[0]["bidPrice"]

        return ask, bid

    @staticmethod
    def send_http_request(func, **kwargs):
        retries_count = -1
        while True:
            retries_count += 1
            try:
                return utils.convert_to_float(func(**kwargs))
            except Exception as e:
                print(e)
                utils.resynch()
                if retries_count < const.MAX_RETRIES:
                    time.sleep(const.SLEEP_TIME)
                else:
                    raise Exception(f"Error: {e}.")
