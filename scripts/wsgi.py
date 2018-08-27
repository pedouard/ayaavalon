#!/usr/bin/env python

import env
from withings.datascience.core import setup_logging
from lib.www.www import app

setup_logging('ws.datascience.ayaaws')

if __name__ == "__main__":
	app.run()

