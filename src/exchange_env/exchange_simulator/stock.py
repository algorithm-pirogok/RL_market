from typing import Tuple, List

from src.exchange_env.exchange_simulator import StockSide

class Stock:
    """
    """
    def __init__(self) -> None:
        self.ask_side = StockSide('Ask')
        self.bid_side = StockSide('Bid')
    
    def execute_orders(self, data):
        for _, row in data.iterrows():
            max_bid = self.bid_side.get_border()
            min_ask = self.ask_side.get_border()

            id = row['NO']
            action = row['BUYSELL']
            type = row['ACTION']
            price = row['PRICE']
            volume = row['VOLUME']
            if type == 1:
                if action == 'B':
                    if price >= min_ask or price == 0:
                        self.ask_side.execute_order(id, volume, price)
                    else:
                        self.bid_side.add_order(id, price, volume)
                elif action == 'S':
                    if price <= max_bid:
                        self.bid_side.execute_order(id, volume, price)
                    else:
                        self.ask_side.add_order(id, price, volume)
            elif type == 0:
                if action == 'B':
                    self.bid_side.remove_order(id, price)
                elif action == 'S':
                    self.ask_side.remove_order(id, price)
    
    def get_volumes(self):
        return self.ask_side.get_volumes(), self.bid_side.get_volumes()
    
    def get_logs(self):
        return self.ask_side.get_logs(), self.bid_side.get_logs()

    def clear_logs(self):
        self.ask_side.clear_logs()
        self.bid_side.clear_logs()

    def view(self) -> Tuple[List[Tuple[float, int]], List[Tuple[float, int]], List[Tuple[int, float, int]]]:
        bid_volumes, bid_logs = self.bid_side.view()
        ask_volumes, ask_logs = self.ask_side.view()
        return ask_volumes, bid_volumes, ask_logs + bid_logs
