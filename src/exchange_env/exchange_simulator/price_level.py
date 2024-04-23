from collections import deque
from typing import Tuple, List, Any

class PriceLevel:
    """
    """
    def __init__(self) -> None:
        self.queue = deque()
        self.total_volume = 0
        self._latest_trades = []

    def add_order(self, id, volume) -> None:
        """
        Execute type 1 order without trade
        """
        self.queue.append((id, volume))
        self.total_volume += volume

    def remove_order(self, id) -> None:
        """
        Execute type 0 order
        """
        for idx, (order_id, volume) in enumerate(self.queue):
            if id == order_id:
                self.total_volume -= volume
                del self.queue[idx]
                return

    def execute_order(self, volume) -> int:
        """
        Execute type 1 order with trade
        """
        while len(self.queue) and volume:
            order_id, order_volume = self.queue.popleft()
            new_volume = volume - order_volume
            if new_volume >= 0:
                volume = new_volume
                self.total_volume -= order_volume
                self._latest_trades.append((order_id, order_volume))
            else:
                order_volume -= volume
                self.total_volume -= volume
                self.queue.appendleft((order_id, order_volume))
                self._latest_trades.append((order_id, volume))
                volume = 0
        return volume

    def get_volume(self):
        return self.total_volume
    
    def get_logs(self):
        return self._latest_trades
    
    def clear_logs(self):
        self._latest_trades = []

    def view(self) -> Tuple[int, List[Any], List[Any]]:
        latest_trades = self._latest_trades
        self._latest_trades = []
        return self.total_volume, latest_trades
