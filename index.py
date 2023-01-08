from flask import Flask, request, current_app, json
import requests


app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/')


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


if __name__ == '__main__':
    app.run()