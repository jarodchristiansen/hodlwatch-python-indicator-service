from flask import Flask, request, current_app, json
from pycoingecko import CoinGeckoAPI
import requests
import pandas as pd
import numpy as np

cg = CoinGeckoAPI()
app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/')
def index():
    return '<h1>Youve reached the hodlwatch indicator service, we arent in right now</h1>'


@app.route('/asset-pair-data')
def assetPairData():
    SERVER_KEY = current_app.config["INIDCATOR_SERVER_KEY"]
    name = request.args.get('name', None)
    sentKey = request.args.get('api_key', None)
    print(sentKey, 'IN ASSET PAIR DATA')

    if not sentKey or sentKey != SERVER_KEY:
        return "Not authorized", 403

    pairData = requests.get(
        'https://min-api.cryptocompare.com/data/top/volumes?tsym={}'.format(name))

    result = app.response_class(
        response=json.dumps(pairData.json()),
        status=200,
        mimetype='application/json'
    )

    return result


@app.route('/asset-price-data')
def asset():
    SERVER_KEY = current_app.config["INIDCATOR_SERVER_KEY"]
    name = request.args.get('name', None)
    time = request.args.get('time', None)
    sentKey = request.args.get('api_key', None)

    print(sentKey)

    if not sentKey or sentKey != SERVER_KEY:
        return "Not authorized", 403

    priceData = requests.get(
        'https://min-api.cryptocompare.com/data/v2/histoday?fsym={}&tsym=USD&limit={}'.format(name, time))

    if name == 'BTC' or name == 'ETH':
        CRYPTO_KEY = current_app.config["CRYPTO_COMPARE_KEY"]

        print(CRYPTO_KEY)

        blockchainData = requests.get(
            'https://min-api.cryptocompare.com/data/blockchain/histo/day?fsym={}&limit={}&api_key={}'.format(name, time, CRYPTO_KEY))

    obs = [priceData.json(), blockchainData.json()]

    result = app.response_class(
        response=json.dumps(obs),
        status=200,
        mimetype='application/json'
    )

    return result


@app.route('/btc-macro-data')
def macroData():
    SERVER_KEY = current_app.config["INIDCATOR_SERVER_KEY"]
    sentKey = request.args.get('api_key', None)

    print(sentKey, 'IN BTC MACRO DATA')

    if not sentKey or sentKey != SERVER_KEY:
        return "Not authorized", 403

    name = 'BTC'
    time = 1827

    priceData = requests.get(
        'https://min-api.cryptocompare.com/data/v2/histoday?fsym={}&tsym=USD&limit={}'.format(name, time)).json()

    df = pd.DataFrame(priceData['Data']['Data'])
    df['totalvolume'] = df['volumefrom'] + df['volumeto']

    volume = df['totalvolume']
    price = df['close']
    time = 365

    df = df.assign(VWAP=((volume * price).cumsum() / volume.cumsum()).ffill())
    df = df.assign(TWAP=(price.cumsum() / len(price)).ffill())
    returns = (df.close - df.close.shift(1))/df.close.shift(1)

    df['returns'] = returns.fillna(0)

    rolling = df['returns'].rolling(window=time)
    rolling_sharpe_s = np.sqrt(time) * (rolling.mean() / rolling.std())

    df['rolling_sharpe'] = rolling_sharpe_s

    result = app.response_class(
        response=json.dumps(df.to_json(orient="records")),
        status=200,
        mimetype='application/json'
    )

    return result


if __name__ == '__main__':
    app.run()
