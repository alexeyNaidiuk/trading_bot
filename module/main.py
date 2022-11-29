import logging
import time

import pandas as pd
from binance.client import Client

from keys import API_KEY, SECRET_KEY

client = Client(API_KEY, SECRET_KEY)


def top_coin():
    all_tickers = pd.DataFrame(client.get_ticker())
    usdt = all_tickers[all_tickers.symbol.str.contains('USDT')]
    work = usdt[~((usdt.symbol.str.contains('UP')) | (usdt.symbol.str.contains('DOWN')))]
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]
    return top_coin


def last_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + 'min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def strategy(buy_amt, SL=0.985, Target=1.02, open_position=False):
    asset = top_coin()
    df = last_data(asset, '1m', '120')

    qty = round(buy_amt / df.Close.iloc[-1], 1)

    if ((df.Close.pct_change() + 1).cumprod()).iloc[-1] > 1:
        print(asset)
        print(df.Close.iloc[-1])
        print(qty)
        order = client.create_order(symbol=asset, side='BUY', type='MARKET', quantity=qty)
        print(order)
        buyprice = float(order['fills'][0]['price'])
        open_position = True

        while open_position:
            try:
                df = last_data(asset, '1m', '2')
            except Exception as error:
                logging.exception(error)
                break

            print(f'Price ' + str(df.Close[-1]))
            print(f'Target ' + str(buyprice * Target))
            print(f'Stop ' + str(buyprice * SL))
            if df.Close[-1] <= buyprice * SL or df.Close[-1] >= buyprice * Target:
                order = client.create_order(symbol=asset, side='SELL', type='MARKET', quantity=qty)
                print(order)
                break
    else:
        print('No find')
        time.sleep(20)
