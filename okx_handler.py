from okx import MarketData
import time, const, utils

class OKXHandler:
    def __init__(self):
        self.okx_api = MarketData.MarketAPI(debug=False)

    def get_most_recent_bid_ask(self, input_symbol):
        data = self.send_http_request(self.okx_api.get_ticker, instId=input_symbol)

        return data[0]['askPx'], data[0]['bidPx']

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