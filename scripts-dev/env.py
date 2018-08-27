# Warning! Edit this file only if you know what you're doing.

# Fix path
import sys
from os.path import dirname, realpath, join, abspath
__basedir__ = abspath(join(dirname(realpath(__file__)), '..'))
sys.path.append(__basedir__)

# Load configuration from files
from withings.datascience.core import DEFAULT_CONFIG_FILES, config
CONFIG_FILES = DEFAULT_CONFIG_FILES + [join(__basedir__, 'datascience.conf')]
config.read(CONFIG_FILES)
