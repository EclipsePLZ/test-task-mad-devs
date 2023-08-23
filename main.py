import json
import logging
import time
import websocket
import asyncio
from collections import deque
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient

MAX_KLINES = 14

TIME_BINANCE = 300


def message_handler(_, message):
    data = json.loads(message)
    klines = data['result']
    print(klines)
    print(klines[:-1])


def on_error(ws, error):
    print('Error:', error)


def on_close(_):
    print("Do custom stuff when connection is closed")


async def start_binance():
    my_client = SpotWebsocketAPIClient(on_message=message_handler,
                                       on_close=on_close)
    while True:
        my_client.klines(symbol="BTCUSDT", interval="1m", limit=MAX_KLINES+1)
        time.sleep(10)


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
