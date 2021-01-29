from flask import Flask
from flask import request
import wireguardian

app = Flask(__name__)

@app.route('/wireguardian', methods=['GET', 'POST'])
def go():    
    if request.method == 'POST':
        if 'pubkey' in request.form:
            clientConfig = wireguardian.createClientConfig(request.form['pubkey'])
            print(clientConfig)
            return '<raw>' + clientConfig.replace('\n', '<br/>') + '</raw>'
    elif request.method == 'GET':
        with open('form.html', 'r') as f:
            return f.read()