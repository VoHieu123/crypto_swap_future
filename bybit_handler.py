from pybit.unified_trading import HTTP
import const, time, utils
import pandas as pd

class BybitHandler:
    def __init__(self):
        self.session = HTTP(testnet=False)

    def get_bid_ask(self, input_symbol_array):
        data = pd.DataFrame()
        for symbol in input_symbol_array:
            send_symbol = symbol
            if symbol == "PEPEUSDT":
                send_symbol = "1000PEPEUSDT"
            if symbol == "LUNAUSDT":
                send_symbol = "LUNA2USDT"
            temp = self.send_http_request(self.session.get_orderbook, category="linear", symbol=send_symbol)
            temp = [[temp["b"][0][0], temp["a"][0][0]]]
            temp = pd.DataFrame(temp, columns=[f"bid_{symbol}", f"ask_{symbol}"])
            data = temp if data.empty else data.join(temp)

        return data

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
