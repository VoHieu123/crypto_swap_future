from pybit.unified_trading import HTTP
import const, time, utils

class BybitHandler:
    def __init__(self):
        self.session = HTTP(testnet=False)

    def get_most_recent_bid_ask(self, input_symbol):
        data = self.send_http_request(self.session.get_orderbook, category="linear", symbol=input_symbol)
        return data["a"][0][0], data["b"][0][0]

    @staticmethod
    def send_http_request(func, **kwargs):
        retries_count = -1
        while True:
            retries_count += 1
            try:
                data = func(**kwargs)
                if data.get("retCode") == 0:
                    return utils.convert_to_float(data["result"])
                else:
                    raise Exception(f"Received corrupted data: {data['msg']}.")
            except Exception as error:
                utils.resynch()
                if retries_count < const.MAX_RETRIES:
                    time.sleep(const.SLEEP_TIME)
                else:
                    raise Exception(f"Error: {error}.")
