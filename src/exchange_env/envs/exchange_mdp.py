from src.exchange_env.exchange_simulator import Exchange, ExchangeDataset, AgentStockManager

path = "stock_20210303.csv"
start_time = "100000000001"
green_stocks = ['GAZP']
red_stocks = None
start_capital = 100000
max_steps = 1000
latency = 0.01

class ExhangeMDP:
    def __init__(self) -> None:
        self._exchange_dataset = ExchangeDataset(path, start_time, green_stocks, red_stocks)
        self._exchange = Exchange(self._exchange_dataset.get_stocks())
        self._agent_stock_manager = AgentStockManager(self._exchange_dataset.get_stocks(), start_capital)
        self._history_volumes = lambda x: x #TODO add history norm

        self._current_step = 1
        self._max_steps = max_steps
        self._latency = latency

    def action(self, action):
        """
        Change enviroment with actions
        """
        pass

    def evaluate(self):
        """
        Get reward
        """
        pass
    
    def is_done(self):
        return self._current_step > self._max_steps

    def observe(self):
        """
        Get state
        """
        volumes = self._exchange.get_volumes()
        parsed_volumes = self._history_volumes(volumes)
        values, orders_info = self._agent_stock_manager.get_info()
        return parsed_volumes, values, orders_info


# todo add params manager
# todo add data parser (add some features)