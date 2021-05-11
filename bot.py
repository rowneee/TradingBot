import cbpro, pprint, talib, numpy, config
from coinbase.wallet.client import Client
from config import api_key, api_secret

RSI_PERIOD = 14
OVERSOLD_THRESHOLD = 30
OVERBOUGHT_THRESHOLD = 70
TRADE_QUANTITY = 0.05
TRADE_SYMBOL = 'ETH-USD'
SOCKET = 'wss://ws-feed.pro.coinbase.com/products/ETH-USA/candles'

public_client = cbpro.PublicClient()
client = Client(api_key, api_secret)
closes = []
in_position = False

class myWebsocketClient(cbpro.WebsocketClient):
    def order(price, size, order_type, product_id):
        try:
            print("sending order")
            order = client.create_order(price=price,
                                        size=TRADE_QUANTITY,
                                        order_type=order_type,
                                        product_id=product_id)
            print("order info")
            print(order)
        except Exception as e:
            print("there was a problem order - {}".format(e))
            return False
        return True

    def on_open(self):
        print('open')

    def on_message(self, message):
        print("public client data")
        pc = public_client.get_product_historic_rates('ETH-USD', granularity=60)
        close = [i[4] for i in pc]
        if close:
            pprint.pprint("candle series {}".format(close))
            closes.append(float(close[-1]))
            print("last close: " + str(pc[-1][4]))
            print('next loop')

            if len(close) > RSI_PERIOD:
                np_closes = numpy.array(close)
                rsi = talib.RSI(np_closes, RSI_PERIOD)
                print("all rsis calculated:")
                print(rsi)
                last_rsi = rsi[-1]
                print("current rsi is {}".format(last_rsi))

                if last_rsi > OVERBOUGHT_THRESHOLD:
                    if in_position:
                        print("Sell!!!!!!")
                        # put sell logic here
                        order_succeeded = order(
                                        size=TRADE_QUANTITY,
                                        order_type='limit',
                                        product_id=TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = False
                    else:
                        print("It's overbought but we don't own any. Nothing to do.")

                if last_rsi < OVERSOLD_THRESHOLD:
                    if in_position:
                        print("It is oversold, but you already own it so nothing to do!")
                    else:
                        print("Buy!!!!!!!")
                        # put order logic here
                        order_succeeded = order(
                            size='0.05',
                            order_type='limit',
                            product_id=TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = True

    def on_close(self):
        print("-- Goodbye! --")


public_client.get_product_historic_rates('ETH-USD', granularity=300)
wsClient = myWebsocketClient(SOCKET, channels=["ticker"])
wsClient.start()