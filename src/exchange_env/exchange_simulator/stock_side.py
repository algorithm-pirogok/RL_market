from collections import defaultdict
from typing import Tuple, List

from sortedcontainers.sortedset import SortedSet as sortedset

from src.exchange_env.exchange_simulator import PriceLevel

class StockSide:
    """
    """
    def __init__(self, type) -> None:
        self.type = type
        self.series = defaultdict(PriceLevel)
        self.prices = sortedset()
        self._used_prices = []
        self._execute_trade = None
    
    def add_order(self, id, price, volume) -> None:
        """
        Execute type 1 order without trade
        """
        self.prices.add(price)
        self.series[price].add_order(id, volume)

    def remove_order(self, id, price) -> None:
        """
        Execute type 0 order
        """
        self.series[price].remove_order(id)
        if not self.series[price].total_volume:
            self.prices.discard(price)
    
    def execute_order(self, id, volume, price) -> Tuple[int, float]:
        """
        Execute type 1 order with trade
        """
        total_cost = 0
        total_volume = 0
        while volume and len(self.prices):
            if self.type == 'Ask':
                current_price = self.prices[0]
                if current_price > price and price != 0:
                    return volume, price
            elif self.type == 'Bid':
                current_price = self.prices[-1]
                if current_price < price and price != 0:
                    return volume, price
            self._used_prices.append(current_price)
            new_volume = self.series[current_price].execute_order(volume)
            if new_volume > 0:
                self.prices.remove(current_price)
            total_volume += volume - new_volume
            total_cost += current_price * (volume - new_volume)
            volume = new_volume
        self._execute_trade = (id, total_cost, total_volume)
        return volume, current_price

    def get_border(self) -> float:
        """
        Get min Ask price and max bid price
        """
        if self.type == 'Ask':
            return self.prices[0] if len (self.prices) > 0 else 1e9
        elif self.type == 'Bid':
            return self.prices[-1] if len (self.prices) > 0 else -100
        else:
            raise ValueError('Error type')
    
    def get_volumes(self):
        volumes = []
        for price in self.prices:
            volume = self.series[price].get_volume()
            volumes.append((price, volume))
        return volumes

    def get_logs(self):
        logs = [self._execute_trade] if self._execute_trade is not None else []
        for price in self._used_prices:
            latest_trades = self.series[price].get_logs()
            for id, trade_volume in latest_trades:
                logs.append((id, price * trade_volume, trade_volume))
        return logs
    
    def clear_logs(self):
        for price in self._used_prices:
            self.series[price].clear_logs()
        self._execute_trade = None
        self._used_prices = []

    def view(self) -> Tuple[List[Tuple[float, int]], List[Tuple[int, float, int]]]:
        """
        Get id's of changes
        """
        logs = [self._execute_trade] if self._execute_trade is not None else []
        volumes = []
        for price in self._used_prices:
            volume, latest_trades = self.series[price].view()
            volumes.append((price, volume))
            for id, trade_volume in latest_trades:
                logs.append((id, price * trade_volume, trade_volume))
        self._execute_trade = None
        self._used_prices = []
        return volumes, logs