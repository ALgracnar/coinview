from flask import Flask, render_template, request, flash, redirect, jsonify
import config, csv, datetime
from binance.client import Client
from binance.enums import *

app = Flask(__name__)
app.secret_key = b'somelongrandomstring'

client = Client(config.API_KEY, config.API_SECRET, tld='com')
# client = Client(tld='us')
from decimal import Decimal as D, ROUND_DOWN, ROUND_UP
import decimal

@app.route('/')
def index():
    title = 'Crypto Monster'
    real_balance=[]
    account = client.get_account()

    balances = account['balances']
    for balance in balances:
        if float(balance['free']) > 0:
            real_balance.append(balance)

    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']

    return render_template('index.html', title=title, my_balances=real_balance, symbols=symbols)


@app.route('/buy', methods=['POST'])
def buy():
    print(request.form)
    try:

        pair=request.form['symbol']
        info = client.get_symbol_info(symbol=pair)
        print(info)
        price_filter = float(info['filters'][0]['tickSize'])
        print(price_filter)
        ticker = client.get_symbol_ticker(symbol=pair)
        print(ticker)
        price = float(ticker['price'])
        price = D.from_float(price).quantize(D(str(price_filter)))
        print(price)
        minimum = float(info['filters'][2]['minQty'])  # 'minQty'
        #quant = D.from_float(price).quantize(D(str(minimum)))
        #print(quant)
        print(price)
        order = client.create_order(symbol=request.form['symbol'],
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=request.form['quantity'])
        print(order)

    except Exception as e:
        print(e)
        app.logger.info(f"exception> {e}")
        flash(e.message, "error")

    return redirect('/')


@app.route('/sell')
def sell():
    return 'sell'


@app.route('/settings')
def settings():
    return 'settings'

@app.route('/history')
def history():
    candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "29 Oct, 2021", "1 Nov, 2021")

    processed_candlesticks = []

    for data in candlesticks:
        candlestick = {
            "time": data[0] / 1000,
            "open": data[1],
            "high": data[2],
            "low": data[3],
            "close": data[4],
            "volume": data[5]
        }


        processed_candlesticks.append(candlestick)
    [print(i)for i in data]
    print('######')
    return jsonify(processed_candlesticks)

if __name__ == '__main__':
	app.run(debug=True)