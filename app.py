import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)


from views import *


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5090, debug=True)
