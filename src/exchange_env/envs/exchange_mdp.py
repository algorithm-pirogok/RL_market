from collections import deque

import pandas as pd

from src.exchange_env.exchange_simulator import Exchange, ExchangeDataset, AgentStockManager
from src.prepare_data import StatsManager

path = "stock_20210303.csv"
start_time = "100000000001"
green_stocks = ['GAZP']
red_stocks = None
start_capital = 100000
max_steps = 1000
latency = 0.01
flow_speed = 1.
depth = 8
max_history = 10
names_for_stats_manager = []
period = 'HOUR'

class ExhangeMDP:
    def __init__(self) -> None:
        self._exchange_dataset = ExchangeDataset(path, start_time, green_stocks, red_stocks)
        self._exchange = Exchange(self._exchange_dataset.get_stocks())
        self._agent_stock_manager = AgentStockManager(self._exchange_dataset.get_stocks(), start_capital)
        self._history_stats = StatsManager(names_for_stats_manager, period)
        self._iterator = iter(self._exchange_dataset.get_data())

        self._current_step = 1
        self._max_steps = max_steps
        self._latency = latency
        self._flow_speed = flow_speed

        self.history_volumes = deque()
        self.history_prices = deque()



    def action(self, action):
        """
        Change enviroment with actions
        """
        # прокрути заявки на биржу, затем посмотри, что изменилось. Го отсюда начинать..
        # То есть нам нужно прокручивать все торги на бирже до тех пор, пока не пройдет  
        # action (seccode, cancel) + (seccode, type, price, volume)
        #нужно добавить итератор и затем крутить заявки до того времени, пока не дойдут до нашего timestamps.
        #после чего добавляем на биржу все наши ордера и возвращаем заявки
        def transform_time_to_int(time):
            hour = int(str(time)[:2])
            minute = int(str(time)[2:4])
            sec = int(str(time)[2:4])
            millisec = int(str(time)[6:9])
            time = (hour * 60 + minute) * 60 + sec + millisec / 1000
            return time

        time = transform_time_to_int(self._exchange_dataset.get_time())
        time_to_execution = time + self._latency
        time_to_end = time = self._flow_speed
        while time < time_to_execution:
            info = next(self._iterator)
            time = transform_time_to_int(info['time'])
            rows = info['rows']
            self._exchange.execute_orders(rows)
        info = next(self._iterator)
        time = transform_time_to_int(info['time'])
        rows = info['rows']
        rows = pd.concat([action, rows], ignore_index = True)
        self._exchange.execute_orders(rows)
        while time < time_to_end:
            info = next(self._iterator)
            time = transform_time_to_int(info['time'])
            rows = info['rows']
            self._exchange.execute_orders(rows)


    def evaluate(self):
        """
        Get reward
        """
        if self._current_step < self._max_steps:
            return 1
        else:
            return 1
    
    def is_done(self):
        ans =  self._current_step > self._max_steps
        self._current_step += 1
        return ans

    def observe(self):
        """
        Get state
        """
        # нужно получить по n слоев с каждого уровня стакана + отнормировать на исторические статистики (нужно считать объем торгов)
        # для объема торгов нужно считать еще объем за каждый час.
        # Вот это го, но как? Давайте смотреть на статистику по дням, например мы берем n дней и по ним смотрим средний объем торгов.
        # Давайте тогда добавим штуку, которая по часу скажет сколько должно быть объема выторговано.
        # Теперь нужно научиться считать час, чтобы доставать статистики
        ask_volumes, bid_volumes = self._exchange.get_volumes()
        current_time, ost_time = self._exchange_dataset.get_period(period)
        historical_stats  = self._history_stats.get_from_time(current_time).drop(columns=['SECCODE'])
        values, orders_info = self._agent_stock_manager.get_info()
        volumes = []
        prices = []
        for ask, bid in zip(ask_volumes, bid_volumes):
            ask_prices, ask_volumes = zip(*sorted(ask)[:depth])
            bid_prices, bid_volumes = zip(*sorted(bid)[-depth:])
            min_ask, max_ask = min(ask_prices), max(ask_prices)
            min_bid, max_bid = min(bid_prices), max(bid_prices)
            volumes.append(bid_volumes+ask_volumes)
            prices.append((min_ask, max_ask, min_bid, max_bid))
        self.history_volumes.append(volumes)
        self.history_prices.append(prices)
        if len(self.history_volumes) > max_history:
            self.history_volumes.popleft()
            self.history_prices.popleft()
        self._exchange.clear_logs()
        # нужно получить время, по времени получить статистики. Затем нужно завести логгер, который будет отслеживать статистику
        return self.history_volumes, self.history_prices, historical_stats, values, orders_info, ost_time
