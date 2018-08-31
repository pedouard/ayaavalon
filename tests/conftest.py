from __future__ import absolute_import

import pytest

from ayaavalon import config


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default='dev',
                     help="Environment in which the tests are executed.")


def pytest_collection_modifyitems(config, items):
    """
    Marking tests for a specific environment is only used with tests executed
    by the deployer (./tests/run_tests.sh).

    If in DEV environment, run all tests. If in prod/beta, run only marked
    tests. Only tests marked with :code:`@pytest.mark.prod` will be executed
    in prod.
    """
    env = config.getoption("--env")
    if env == "dev":
        return

    skip = pytest.mark.skip(
        reason="Test not marked to be executed in {env}".format(env=env)
    )

    necessary_markers = {"prod"}
    if env == "beta":
        necessary_markers.add("beta")

    for item in items:
        if not necessary_markers.intersection(item.keywords):
            item.add_marker(skip)


# Remove all configuration and replace it by the test configuration.
# Only the sections prefixed with "test:" (which is removed afterwards) are
# used. Example:
# [ayaavalon]
# db_uri = XXX
# param = 10
# [test:ayaavalon]
# db_uri = YYY
#
# >>> config.get('ayaavalon', 'db_uri')
# 'YYY'
# >>> config.get('ayaavalon', 'param')
# NoOptionError: No option 'param' in section: 'ayaavalon'
test_sections = {}
for section in config.sections():
    if section.startswith('test:'):
        test_sections[section[5:]] = list(config.items(section))
    config.remove_section(section)

for section, options in test_sections.items():
    config.add_section(section)
    for name, value in options:
        config.set(section, name, value)

