from flask import Flask, request, current_app, json

import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
app.config.from_pyfile('config.py')


@app.route('/btc-macro-data')
def macroData():
    SERVER_KEY = current_app.config["INIDCATOR_SERVER_KEY"]
    sentKey = request.args.get('api_key', None)

    if not sentKey or sentKey != SERVER_KEY:
        return "Not authorized", 403

    priceData = requests.get(
        'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=1827').json()

    df = pd.DataFrame(priceData['Data']['Data'])


    df = df.assign(VWAP=(((df['volumefrom'] + df['volumeto']) * df['close']).cumsum() / (df['volumefrom'] + df['volumeto']).cumsum()).ffill())
    df = df.assign(TWAP=(df['close'].cumsum() / len(df['close'])).ffill())

    rolling = ((df.close - df.close.shift(1))/df.close.shift(1)).fillna(0).rolling(window=365)
    df['rolling_sharpe'] = np.sqrt(365) * (rolling.mean() / rolling.std())

    result = app.response_class(
        response=json.dumps(df.to_json(orient="records")),
        status=200,
        mimetype='application/json'
    )

    return result


if __name__ == '__main__':
    app.run()
