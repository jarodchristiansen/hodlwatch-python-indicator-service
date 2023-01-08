from flask import Flask, request, current_app, json
from pycoingecko import CoinGeckoAPI
import requests


cg = CoinGeckoAPI()
app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/')
def index():
    return '<h1>Hello Puppy!</h1>'


@app.route('/information')
def info():
    return "<h1>Puppies are cute</h1>"


@app.route('/asset')
def asset():
    name = request.args.get('name', None)
    time = request.args.get('time', None)

    print('IN Asset NAME', name, time)

    priceData = requests.get(
        'https://min-api.cryptocompare.com/data/v2/histoday?fsym={}&tsym=USD&limit={}'.format(name, time))

    if name == 'BTC' or name == 'ETH':
        CRYPTO_KEY = current_app.config["CRYPTO_COMPARE_KEY"]

        print(CRYPTO_KEY)

        blockchainData = requests.get(
            'https://min-api.cryptocompare.com/data/blockchain/histo/day?fsym={}&limit={}&api_key={}'.format(name, time, CRYPTO_KEY))

    #   let priceData = await fetch(
    #     `https://min-api.cryptocompare.com/data/v2/histoday?fsym=${symbol.toUpperCase()}&tsym=USD&limit=${time}`
    #   ).then((response) => response.json());

    obs = [priceData.json(), blockchainData.json()]

    result = app.response_class(
        response=json.dumps(obs),
        status=200,
        mimetype='application/json'
    )

    return result


if __name__ == '__main__':
    app.run()
