import json
import time
import asyncio
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
import pandas_ta as pta
import pandas as pd
import datetime


MAX_KLINES = 14
TIME_BINANCE = 300
INTERVAL_BINANCE = '5m'
CURRENCY_PAIR_BINANCE = 'BTCUSDT'


def message_handler(_, message):
    data = json.loads(message)

    # The closing price is at position 4
    # To get completely closed candles we remove the last candle
    # To calculate RSI with length = 14, we need 15 candles
    klines_close_prices = [float(kline_info[4]) for kline_info in data['result'][:-1]]
    rsi_index = pta.rsi(close=pd.Series(klines_close_prices), length=14).values[-1]

    print('Binance:')
    print(f'Time: {datetime.datetime.now()}')
    print(f'RSI ({CURRENCY_PAIR_BINANCE}): {rsi_index}')
    print()


def on_error(ws, error):
    print('Error:', error)


def on_close(_):
    print("Do custom stuff when connection is closed")


async def start_binance():
    my_client = SpotWebsocketAPIClient(on_message=message_handler,
                                       on_close=on_close)
    while True:
        my_client.klines(symbol=CURRENCY_PAIR_BINANCE, interval=INTERVAL_BINANCE, limit=MAX_KLINES + 2)
        time.sleep(TIME_BINANCE)


def start_tasks():
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(start_binance())]
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Manually closed application')
    finally:
        loop.close()
        print('App is closed')


if __name__ == '__main__':
    start_tasks()
