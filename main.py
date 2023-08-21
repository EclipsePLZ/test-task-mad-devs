import json
import logging
import time
import websocket
import threading


def on_message(ws, message):
    data = json.loads(message)
    if 'k' in data and data['k']['c'] != '0':
        kline_data = data['k']
        print('Binance:')
        print('Open time:', kline_data['t'])
        print()

def on_error(ws, error):
    print('Error:', error)


def on_close(ws, close_status_code, close_msg):
    print('Closed:', close_status_code, close_msg)


def on_open(ws):
    payload = {
        'method': 'SUBSCRIBE',
        'params': [
            'btcusdt@kline_1s'
        ],
        'id': 1
    }
    ws.send(json.dumps(payload))


def message_handler(_, message):
    print(message)


def get_binance():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp('wss://stream.binance.com:9443/ws/btcusdt@kline_1s', on_message=on)


if __name__ == '__main__':
    get_binance()
