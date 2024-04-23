from typing import List

from src.exchange_env.exchange_simulator import Stock

class Exchange:
    """
    """
    def __init__(self, names: List[str]) -> None:
        self.stocks = {name: Stock() for name in names}
    
    def execute_orders(self, rows):
        for name, group in rows.groupby(['SECCODE']):
            name = name[0]
            self.stocks[name].execute_orders(group)

    def get_volumes(self):
        ask_volumes = [] 
        bid_volumes = [] 
        for stock in self.stocks.values():
            ask, bid = stock.get_volumes()
            ask_volumes.append(ask)
            bid_volumes.append(bid)
        return ask_volumes, bid_volumes

    def get_logs(self):
        ask_logs = {}
        bid_logs = {}
        for name, stock in self.stocks.items():
            ask_logs[name], bid_logs[name] = stock.get_logs()
        return ask_logs, bid_logs

    def clear_logs(self):
        for name in self.stocks:
            self.stocks[name].clear_logs()

    def view(self):
        ask_volumes = [] 
        bid_volumes = [] 
        trades_logs = []
        for name, stock in self.stocks.items():
            a, b, t = stock.view()
            ask_volumes.append(a)
            bid_volumes(b)
            trades_logs.extend(t)
