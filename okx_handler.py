from okx import PublicData
import time, const, utils
import pandas as pd

class OKXHandler:
    def __init__(self):
        self.okx_api = PublicData.PublicAPI(debug=False)

    def get_most_recent_bid_ask(self, input_symbol_array):
        data = pd.DataFrame()

        for input_symbol in input_symbol_array:
            temp = self.send_http_request(self.okx_api.get_ticker, instId=input_symbol)
            if len(temp["data"]) != 0:
                temp = pd.DataFrame(temp["data"])
                temp = temp[["askPx", "bidPx"]]
                temp.rename(columns = {"bidPx" : "bid_" + input_symbol}, inplace = True)
                temp.rename(columns = {"askPx" : "ask_" + input_symbol}, inplace = True)
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
                data = func(**kwargs)
                if data.get("code") == "0":
                    return utils.convert_to_float(data["data"])
                else:
                    raise Exception(f"Received corrupted data: {data['msg']}.")
            except Exception as error:
                utils.resynch()
                if retries_count < const.MAX_RETRIES:
                    time.sleep(const.SLEEP_TIME)
                else:
                    raise Exception(f"Error: {error}.")