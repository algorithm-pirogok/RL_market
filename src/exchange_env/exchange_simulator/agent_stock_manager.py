import numpy as np

class AgentStockManager:
    def __init__(self, names, start_capital: float) -> None:
        self.values = {name: 0. for name in names}
        self.capital = start_capital
        self.orders = {name: dict() for name in names}
    
    def add_info(self, information):
        """
        Info for adding orders
        """
        for name, logs in information.items():
           id, price, volume = logs
           self.orders[name][id] = (price, volume)
    
    def remove_info(self, information):
        """
        Info for erase orders
        """
        for name, id in information.items():
            del self.orders[name][id]
    
    def update_info(self, ask_information, bid_information):
        for name, logs in ask_information.items():
            id, price, trade_volume = logs
            if not id in ask_information[name]:
                continue
            self.values[name] -= trade_volume
            self.capital += price

            volume = ask_information[name][id]
            del ask_information[name][id]
            if volume > trade_volume:
                ask_information[name][id] = volume - trade_volume
        
        for name, logs in bid_information.items():
            id, price, trade_volume = logs
            if not id in bid_information[name]:
                continue
            self.values[name] += trade_volume
            self.capital -= price

            volume = bid_information[name][id]
            del bid_information[name][id]
            if volume > trade_volume:
                bid_information[name][id] = volume - trade_volume

    def get_info(self):
        values = self.values.values() + [self.capital]
        orders_info = []
        for dt in self.orders.values():
            lst = [price * volume for (price, volume) in dt.values()]
            count = len(lst)
            mean = np.mean(lst)
            std = np.std(lst)
            orders_info.extend([count, mean, std])
        return values, orders_info
