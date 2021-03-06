import websocket, json, pprint
import config
from binance.client import Client
from binance.enums import *
import EMA


SOCKET = "wss://stream.binance.com:9443/ws/stream?streams=dotusdt@kline_3m/dotusdt@kline_1m"


TRADE_SYMBOL = 'DOTUSDT'
TRADE_QUANTITY = 0.05

closes = []
closes1= []
oneema3=[]
oneema9=[]
threeema3=[]
threeema9=[]
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes,closes1, in_position,oneema9,threeema3,threeema9
    

    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['data']["k"]

    is_candle_closed = candle['x']
    close = candle['c']
    

    
    if is_candle_closed:
        if json_message["stream"]=="dotusdt@kline_1m":
            closes1.append(float(close))
        
        if json_message["stream"]=="dotusdt@kline_3m":      
            closes.append(float(close))

        
        oneema3.append(EMA.ema(closes1,3))
        oneema9.append(EMA.ema(closes1,9))
        threeema3.append(EMA.ema(closes,3))
        threeema9.append(EMA.ema(closes,9))

        
        if threeema3[-1] > threeema9[-1]:

            if oneema3[-1] > oneema9[-1]:
                print("Oversold! Buy! Buy! Buy!")
                # put binance buy order logic here
                order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    in_position = True

                if oneema3[-1]< oneema9[-1]:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    in_position = False

       
                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
   
        

    
    

        
    
        
                
