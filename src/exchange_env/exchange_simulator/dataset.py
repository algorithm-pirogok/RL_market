import pandas as pd


class ExchangeDataset:
    def __init__(self, path: str, start_time: int = None, green_stocks = None, red_stocks = None) -> None:
        self._logs = pd.read_csv(f"data/csv/{path}").drop(columns=['ORDERNO', 'TRADENO', 'TRADEPRICE'])
        self.find_anomaly_and_fix()
        self._logs = self._logs[self._logs.ACTION != 2]
        if start_time is not None:
            self._logs = self._logs[self._logs.TIME >= start_time]
        if green_stocks is not None:
            self._logs = self._logs[self._logs.SECCODE.isin(green_stocks)].reset_index(drop=True)
        elif red_stocks is not None:
            self._logs = self._logs[~self._logs.SECCODE.isin(red_stocks)].reset_index(drop=True)

        self._stock_names = self._logs.SECCODE.unique()
        self._current_time = self._logs.TIME.iloc[0]
        self._logs = self._logs.groupby('TIME')
    
    def get_stocks(self):
        return self._stock_names

    def get_time(self):
        return self._current_time

    def get_period(self, mode):
        hour = int(str(self._current_time)[0:2])
        minute = int(str(self._current_time)[2:4])
        if mode == 'HOUR':
            return hour, minute
        elif mode == 'HALF_OF_HOUR':
            return hour * 2 + (minute >= 30), minute % 30
        elif mode == 'QUARTER_OF_HOUR':
            return hour * 4 + minute // 15, minute % 15

    def _convert_time(self, x: str):
        return (int(x[0:2]) * 3600 + int(x[2:4]) * 60 + int(x[4:6])) * pow(10, len(x[6:])) + int(x[6:])

    def find_anomaly_and_fix(self):
        self.find_market_deal_with_zero_type()
        self.find_icebers()
    
    def find_market_deal_with_zero_type(self):
        #TODO 
        pass
    
    def find_icebers(self):
        #TODO
        pass

    def __len__(self):
        return len(self._logs)

    def get_data(self):
        for time, data in self._logs:
            rows = data
            self._current_time = time
            yield {
                'time': time,
                'rows': rows
            }
