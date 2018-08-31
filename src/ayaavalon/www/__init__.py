from flask import Flask
from flask_autodoc import Autodoc
from withings.datascience.core.flask_utils import init_statsd, nocache, \
    handle_bad_request, handle_exceptions


app = Flask(__name__)
auto = Autodoc(app)
app.errorhandler(404)(handle_bad_request)
app.errorhandler(422)(handle_bad_request)
app.errorhandler(500)(handle_bad_request)
init_statsd(app)

import ayaavalon.www.player
import ayaavalon.www.game
import ayaavalon.www.stats
