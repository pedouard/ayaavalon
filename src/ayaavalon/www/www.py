# -*- coding: UTF-8 -*

import os
from functools import wraps

from flask import Flask, send_file, url_for, redirect
from flask_autodoc import Autodoc
from webargs import fields
from webargs.flaskparser import use_kwargs
from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions

from ayaavalon.database import session
from ayaavalon.www import app, auto



def rollback_on_exception(func):
    @wraps(func)
    def dec(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            session.rollback()
            raise
    return dec


@app.route("/")
@nocache
@handle_exceptions
def home():
    __dir__ = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(__dir__, "static/index.html")
    return redirect(url_for("static", filename="index.html"))

""" Import routes """

@app.route('/doc')
def documentation():
    return auto.html()


@auto.doc()
@app.route('/image/get')
@nocache
@use_kwargs({
    'name': fields.Str(required=True),
    })
@handle_exceptions
def image_get(name):
    __dir__ = os.path.dirname(os.path.realpath(__file__))
    __dir__ = os.path.join(__dir__, "img")
    path = os.path.join(__dir__, name)
    return send_file(path, mimetype='image/png')

