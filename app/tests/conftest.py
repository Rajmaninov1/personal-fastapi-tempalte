import os


def pytest_configure(config):
    # Set only necessary or env vars without default value. Example:
    os.environ['SERVICE_NAME'] = 'test'
