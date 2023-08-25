import json
import asyncio
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
import pandas_ta as pta
import pandas as pd
import datetime
from bfxapi import Client, PUB_WSS_HOST


MAX_KLINES_BINANCE = 14
MAX_KLINES_BITFINEX = 1
TIME_BINANCE = 300
TIME_BITFINEX = 60
INTERVAL_BINANCE = '5m'
INTERVAL_BITFINEX = '1m'
CURRENCY_PAIR_BINANCE = 'BTCUSDT'
CURRENCY_PAIR_BITFINEX = 'tBTCUSD'

bfx = Client(wss_host=PUB_WSS_HOST)


def message_handler(_, message):
    data = json.loads(message)

    # The closing price is at position 4
    # To get completely closed candles we remove the last candle
    # To calculate RSI with length = 14, we need 15 candles
    klines_close_prices = [float(kline_info[4]) for kline_info in data['result'][:-1]]
    rsi_index = pta.rsi(close=pd.Series(klines_close_prices), length=14).values[-1]

    print('Binance:')
    print(f'Time: {datetime.datetime.now().replace(microsecond=0)}')
    print(f'RSI ({CURRENCY_PAIR_BINANCE}): {rsi_index}')
    print(f'Close price for the last closed candle: {klines_close_prices[-1]}')
    print()


async def start_binance():
    my_client = SpotWebsocketAPIClient(on_message=message_handler)
    while True:
        my_client.klines(symbol=CURRENCY_PAIR_BINANCE, interval=INTERVAL_BINANCE, limit=MAX_KLINES_BINANCE + 2)
        await asyncio.sleep(TIME_BINANCE)


async def start_bitfinex():
    while True:
        # To get completely closed candles we remove the last candle
        # To calculate VWAP last closed candle we need two last closed candles
        last_candles = bfx.rest.public.get_candles_hist(tf=INTERVAL_BITFINEX,
                                                        symbol=CURRENCY_PAIR_BITFINEX,
                                                        limit=MAX_KLINES_BITFINEX+2)[1:]
        last_candles.reverse()

        # In this api timestamp is given in milliseconds, so it should be converted to seconds
        index_datetime = [datetime.datetime.fromtimestamp(lst_candle.mts / 1000) for lst_candle in last_candles]

        high_series = pd.Series([lst_candle.high for lst_candle in last_candles], index=index_datetime)
        low_series = pd.Series([lst_candle.low for lst_candle in last_candles], index=index_datetime)
        close_series = pd.Series([lst_candle.close for lst_candle in last_candles], index=index_datetime)
        volume_series = pd.Series([lst_candle.volume for lst_candle in last_candles], index=index_datetime)

        # VWAP index for last candle at the last position
        vwap_index = pta.vwap(high=high_series,
                              low=low_series,
                              close=close_series,
                              volume=volume_series).values[-1]

        print('Bitfinex:')
        print(f'Time: {datetime.datetime.now().replace(microsecond=0)}')
        print(f'VWAP ({CURRENCY_PAIR_BITFINEX}): {vwap_index}')
        print(f'Close price for the last closed candle: {close_series.values[-1]}')
        print()

        await asyncio.sleep(TIME_BITFINEX)


async def start_tasks():
    awaitable_obj = asyncio.gather(start_bitfinex(), start_binance())

    await awaitable_obj


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(start_tasks())
        loop.run_forever()
    except KeyboardInterrupt:
        print('Manually closed application')
    finally:
        loop.close()
        print('App is closed')
