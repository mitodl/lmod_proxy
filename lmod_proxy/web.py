# -*- coding: utf-8 -*-
"""Root flask application for lmod_proxy"""

from flask import Flask

from lmod_proxy import __project__
from lmod_proxy.edx_grades import edx_grades

app = Flask(__project__)
app.config.from_object('lmod_proxy.config'.format(__project__))

app.register_blueprint(edx_grades, url_prefix='/edx_grades')


@app.route('/', methods=['GET'])
def index():
    """Welcome them to our amazing LMod Proxy

    Return:
        Flask.response
    """
    return '<h1>Welcome to LMod-Proxy'
