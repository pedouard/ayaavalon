#!/usr/bin/env python
# -*- coding: utf-8 -*-

import env
from withings.datascience.core import setup_logging
from lib.www.www import app

setup_logging('ws.datascience.ayaavalon')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=6444)

