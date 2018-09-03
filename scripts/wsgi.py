#!/usr/bin/env python

import env
from withings.datascience.core import setup_logging
from ayaavalon.www.www import app

setup_logging('ws.datascience.ayaavalon')

if __name__ == "__main__":
    app.run()

