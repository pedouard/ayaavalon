# -*- coding: UTF-8 -*

import os
import random
from flask import Flask, Response
from webargs import fields
from webargs.flaskparser import use_kwargs
from flask.ext.autodoc import Autodoc
from flask import send_file
from lib.db import database
from functools import wraps

from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions, json_response, WithingsException
from withings.api import WithingsAPI
from withings.datascience.core import config

import status

app = Flask(__name__)
auto = Autodoc(app)
app.errorhandler(404)(handle_bad_request)
app.errorhandler(422)(handle_bad_request)
app.errorhandler(500)(handle_bad_request)
init_statsd(app)

session = database.session()
api = WithingsAPI(auto_logout=False)

def rollback_on_exception(func):
    @wraps(func)
    def dec(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            session.rollback()
            raise
    return dec

def check_groupid(func):
    @wraps(func)
    def dec(*args, **kwargs):
        if "groupid" not in kwargs or kwargs["groupid"] != config.get('ayaa', 'groupid'):
            raise WithingsException(*status.INVALID_GROUPID)

        del(kwargs["groupid"])

        try:
            return func(*args, **kwargs)
        except Exception, e:
            session.rollback()
            raise
    return dec

@app.route("/")
@nocache
@handle_exceptions
def home():
    return json_response({"status": 0, "body": "AYAA!"})

""" Import routes """

@app.route('/doc')
def documentation():
    return auto.html()

@auto.doc()
@app.route('/survey/get')
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    })
@handle_exceptions
@check_groupid
def get_survey():
    questions = [
        #{
        #    "choice1": "dans les hauteurs",
        #    "conjunction": "ou",
        #    "choice2": "terre à terre",
        #    "clue": "Votre cible est plus %s que %s",
        #    "profile": "Vous êtes plus %s que %s",
        #    "img1": None,
        #    "img2": None,
        #},
        {
            "choice1": "thé",
            "conjunction": "ou",
            "choice2": "café",
            "clue": "Votre cible est plutôt %s que %s",
            "profile": "Vous êtes plutôt %s que %s",
            "img1": "the.png",
            "img2": "cafe.png",
        },
        {
            "choice1": "Gryffondor",
            "conjunction": "ou",
            "choice2": "Serpentard",
            "clue": "Votre cible est plutôt %s que %s",
            "profile": "Vous êtes plutôt %s que %s",
            "img1": "gryffondor.png",
            "img2": "serpentard.png",
        },
        {
            "choice1": "marathon",
            "conjunction": "ou",
            "choice2": "barathon",
            "clue": "Votre cible est plus %s que %s",
            "profile": "Vous êtes plus %s que %s",
            "img1": "marathon.png",
            "img2": "barathon.png",
        },
        {
            "choice1": "chocolatine",
            "conjunction": "ou",
            "choice2": "pain au chocolat",
            "clue": "Votre cible dirait plus %s que %s",
            "profile": "Vous diriez plus %s que %s",
            "img1": "chocolatine.png",
            "img2": "painauchocolat.png",
        },
        #{
        #    "choice1": "opérationnel",
        #    "conjunction": "ou",
        #    "choice2": "technique",
        #    "clue": "Votre cible est plus %s que %s",
        #    "profile": "Vous êtes plus %s que %s",
        #    "img1": None,
        #    "img2": None,
        #},
        {
            "choice1": "Japonais",
            "conjunction": "ou",
            "choice2": "Big Fernand",
            "clue": "A midi, votre cible est plus %s que %s",
            "profile": "Pour vous, midi c'est plus %s que %s",
            "img1": "japonais.png",
            "img2": "bigfernand.png",
        },
        #{
        #    "choice1": "cantine",
        #    "conjunction": "ou",
        #    "choice2": "plat maison",
        #    "clue": "A midi, votre cible est plus %s que %s",
        #    "profile": "Pour vous, midi c'est plus %s que %s",
        #    "img1": None,
        #    "img2": None,
        #},
        {
            "choice1": "fêtard(e)",
            "conjunction": "ou",
            "choice2": "couche tôt",
            "clue": "Votre cible est plus %s que %s",
            "profile": "Vous êtes plus %s que %s",
            "img1": "fetard.png",
            "img2": "couchetot.png",
        },
        {
            "choice1": "métro",
            "conjunction": "ou",
            "choice2": "vélo",
            "clue": "Votre cible est plutôt %s que %s",
            "profile": "Vous êtes plus %s que %s",
            "img1": "metro.png",
            "img2": "velo.png",
        },
        {
            "choice1": "à moitié vide",
            "conjunction": "ou",
            "choice2": "à moitié plein",
            "clue": "Votre cible voit le verre %s plus qu'%s",
            "profile": "Vous voyez le verre %s plus qu'%s",
            "img1": "half_empty.png",
            "img2": "half_full.png",
        },
        {
            "choice1": "Art Abstrait",
            "conjunction": "ou",
            "choice2": "Réalisme",
            "clue": "Votre cible est plus %s que %s",
            "profile": "Vous êtes plus %s que %s",
            "img1": "abstrait.png",
            "img2": "realisme.png",
        },
        {
            "choice1": "chien",
            "conjunction": "ou",
            "choice2": "chat",
            "clue": "Votre cible est plutôt %s que %s",
            "profile": "Vous êtes plutôt %s que %s",
            "img1": "dog.png",
            "img2": "cat.png",
        },
        #{
        #    "choice1": "escaliers",
        #    "conjunction": "ou",
        #    "choice2": "ascenseur",
        #    "clue": "Votre cible est plutôt %s qu'%s",
        #    "profile": "Vous êtes plutôt %s qu'%s",
        #    "img1": None,
        #    "img2": None,
        #},
        {
            "choice1": "Professeur Tournesol",
            "conjunction": "ou",
            "choice2": "Capitaine Haddock",
            "clue": "Votre cible est plus %s que %s",
            "profile": "Vous êtes plus %s que %s",
            "img1": "tournesol.png",
            "img2": "haddock.png",
        },
        {
            "choice1": "James Bond",
            "conjunction": "ou",
            "choice2": "Austin Powers",
            "clue": "Votre cible est plus %s que %s",
            "profile": "Vous êtes plus %s que %s",
            "img1": "james_bond.png",
            "img2": "austin_powers.png",
        },
        {
            "choice1": "Mozart",
            "conjunction": "ou",
            "choice2": "Skrillex",
            "clue": "Votre cible est plus %s que %s",
            "profile": "Vous êtes plus %s que %s",
            "img1": "mozart.png",
            "img2": "skrillex.png",
        },
        {
            "choice1": "Android",
            "conjunction": "ou",
            "choice2": "iOS",
            "clue": "Votre cible est plutôt %s que %s",
            "profile": "Vous êtes plutôt %s que %s",
            "img1": "android.png",
            "img2": "ios.png",
        },
        {
            "choice1": "Carapuce",
            "conjunction": "ou",
            "choice2": "Salameche",
            "clue": "Votre cible est plutôt %s que %s",
            "profile": "Vous êtes plutôt %s que %s",
            "img1": "carapuce.png",
            "img2": "salameche.png",
        },
        {
            "choice1": "Withings",
            "conjunction": "ou",
            "choice2": "Nokia",
            "clue": "Votre cible est plutôt %s que %s",
            "profile": "Vous êtes plutôt %s que %s",
            "img1": "withings.png",
            "img2": "nokia.png",
        }
    ]
    for q in questions:
        if q["img1"] is not None:
            q["img1"] = "https://ayaaws.corp.withings.com/image/get?groupid=%s&name=%s" % (
                config.get('ayaa', 'groupid'), q["img1"])

        if q["img2"] is not None:
            q["img2"] = "https://ayaaws.corp.withings.com/image/get?groupid=%s&name=%s" % (
                config.get('ayaa', 'groupid'), q["img2"])

    random.shuffle(questions)

    return json_response({
        "status": 0,
        "body": {
            "questions": questions[:8]
            }
        })

@auto.doc()
@app.route('/image/get')
@nocache
@use_kwargs({
    'groupid': fields.Str(required=True),
    'name': fields.Str(required=True),
    })
@handle_exceptions
@check_groupid
def image_get(name):
    __dir__ = os.path.dirname(os.path.realpath(__file__))
    __dir__ = os.path.join(__dir__, "img")
    path = os.path.join(__dir__, name)
    return send_file(path, mimetype='image/png')

import player, contract, game

"""
Récap des points qu'on a noté au tableau:
- Add text explaining how to kill & text explaining how often clues are unlocked
"""
