import pandas as pd

class StatsManager:
    def __init__(self, names, period) -> None:
        self._mean_dataset = pd.concat([pd.read_csv(f'data/statistics/{name}_{period}.csv', index_col=0) 
                                        for name in names]).groupby(['SECCODE', period]).mean().reset_index()

    def get_from_time(self, time):
        return self._mean_dataset[self._mean_dataset.HOUR == time].drop(columns=['HOUR'])
