import argparse
import pandas as pd

def get_stats(name_of_file) -> None:
    data = pd.read_csv('data/csv/{name_of_file}')
    data = data[data.ACTION == 2].drop(columns=['ACTION', 'NO', 'TRADENO', 'TRADEPRICE', 'ORDERNO'])
    data['HOUR'] = data.TIME.apply(lambda x: int(str(x)[:2]))
    data['MINUTE'] = data.TIME.apply(lambda x: int(str(x)[2:4]))
    data['HALF_OF_HOUR'] = data['HOUR'] * 2 + (data['MINUTE'] >= 30)
    data['QUARTER_OF_HOUR'] = data['HOUR'] * 4 + (data['MINUTE'] // 15)
    data = data.drop(columns=['TIME', 'MINUTE'])
    for period in ['HOUR', 'HALF_OF_HOUR', 'QUARTER_OF_HOUR']:
        df = data.groupby(['SECCODE', 'BUYSELL', period]).agg({'PRICE': ['mean', 'sum', 'std', 'count'], 'VOLUME': ['mean', 'sum', 'std', 'count']}).unstack(fill_value=None).stack(level=2, dropna=False)
        df.columns = [f'{cat}_{stat}' for cat, stat in df.columns]
        df.fillna({col: 0 for col in ['PRICE_std', 'PRICE_sum', 'PRICE_count', 'VOLUME_mean', 'VOLUME_sum', 'VOLUME_std', 'VOLUME_count']}, inplace=True)
        df['PRICE_mean'] = df['PRICE_mean'].ffill().bfill()
        df = df.reset_index()
        df.to_csv(f'data/statistics/{name_of_file}_{period}.csv')
    print('Stats computed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple example with argparse.')
    parser.add_argument('name_of_file', help='Input name of file which you want to get stats')
    args = parser.parse_args()
    get_stats(args.name_of_file)
