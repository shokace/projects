from flask import Flask, render_template, request, abort
import datetime as datetime
import datafetch
import dataplot
import hmac
import hashlib
import subprocess
import dotenv import load_dotenv
import os



app = Flask(__name__)

# CoinGecko API endpoint for top 100 cryptocurrencies
tm_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"

#Github key comes from the .env file
load_dotenv()
GITHUB_SECRET = os.getenv('GITHUB_KEY').encode()
REPO_PATH = os.getenv('REPO_PATH')

# Fetch data
try:
    crypto_data = datafetch.fetch_crypto_data(tm_url)
    top_crypto = datafetch.top_mover(crypto_data)
    #print(top_crypto)
except Exception as _:
    print("Base data could not be fetched.")




# Find the top mover
if crypto_data:
    if top_crypto:
        crypto_name = top_crypto['id']
        #print(crypto_name)
        granular_data = datafetch.fetch_granular_data(crypto_name)
        
        #print(granular_data)
        fig = dataplot.plotdata(crypto_name, granular_data)
    else:
        print("No top mover found.")
else:
    print("Failed to fetch data.")



#init render template
@app.route('/')
def index():
    return render_template('index.html', graph_html=fig)


@app.route('/webhook', methods=['POST'])
def webhook():
    # Validate the request
    signature = request.headers.get('X-Hub-Signature')
    sha_name, signature = signature.split('=')
    if sha_name != 'sha1':
        abort(501)

    # HMAC requires the key to be bytes, but data is string
    mac = hmac.new(GITHUB_SECRET, msg=request.data, digestmod=hashlib.sha1)

    # Verify the signature
    if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
        abort(403)

    # If the signature is valid, pull the latest code and restart the application
    subprocess.call(['/bin/bash', f'{REPO_PATH}/../deploy.sh'])   

    return 'OK', 200



if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8000)





