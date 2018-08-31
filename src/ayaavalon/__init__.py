import os.path

try:
    from withings.datascience.core import DEFAULT_CONFIG_FILES, config
except ImportError:
    try:
        from configparser import ConfigParser
    except ImportError:
        from ConfigParser import SafeConfigParser as ConfigParser

    config = ConfigParser()
    DEFAULT_CONFIG_FILES = []

LOCAL_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.realpath(__file__)
    ))),
    'datascience.conf'
)

config.read(DEFAULT_CONFIG_FILES + [LOCAL_CONFIG_PATH])

# /!\ WARNING: Do *NOT* import anything else after setting up the config /!\
# The tests suppose that nothing has used the config yet. Any code past this
# is not guaranteed to use the proper configuration when executing the tests.
# YOU HAVE TO ENSURE IT YOURSELF.
