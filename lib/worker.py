# -*- coding: utf-8 -*-

from withings.datascience.core.workers import MultiBeanstalkWorker, TemporaryError
import logging
import lib.utils

class ExampleWorker(MultiBeanstalkWorker):

    schema = {
        "properties": {
            "event": {"enum": ["add"]},
            "args": {
                "properties": {
                    "x": {"type": "int"},
                    "y": {"type": "int"},
                },
                "required": ["x", "y"],
            },
            "required": ["event", "args"]
        }
    }

    def job(self, task):
        event = task['event']
        args = task['args']

        if event == 'add':
            x = args['x']
            y = args['y']
            z = lib.utils.add(x, y)
            logging.info('Result: %d + %d =  %d', x, y, z)

    def handle_exception(self, e, job):
        if isinstance(e, TemporaryError):
            job.release(delay=60)
        else:
            job.bury()
