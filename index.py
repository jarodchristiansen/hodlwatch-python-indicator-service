from flask import Flask, request, current_app

import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
app.config.from_pyfile('config.py')


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
