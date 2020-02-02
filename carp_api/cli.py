import importlib
import os
import sys

from flask.cli import main as flask_main


def check_variables():
    if "SIMPLE_SETTINGS" in os.environ:
        print(
            "SIMPLE_SETTINGS set to '{}'".format(
                os.environ['SIMPLE_SETTINGS']))

    else:
        os.environ['SIMPLE_SETTINGS'] = 'carp_api.settings.base'

        print(
            "SIMPLE_SETTINGS not set, default in use '{}'".format(
                os.environ['SIMPLE_SETTINGS']))

    if "FLASK_APP" in os.environ:
        print(
            "FLASK APP set to '{}'".format(os.environ['FLASK_APP']))

    else:
        os.environ['FLASK_APP'] = (
            'carp_api.server_factory.server_factory:create_app'
        )

        print(
            "FLASK_APP not set, default in use '{}'".format(
                os.environ['FLASK_APP']))


def check_settings():
    try:
        from carp_api.settings.base import APP_NAME

        print(f"Base settings are importable - AppName: {APP_NAME}")
    except ImportError as err:
        print(err)
        print("(ERROR) Unable to load settings")
        sys.exit(1)

    try:
        module = importlib.import_module(os.environ['SIMPLE_SETTINGS'])

        app_name = module.APP_NAME

        print(f"Application settings are importable - AppName: {app_name}")
    except ModuleNotFoundError as err:
        print(err)
        print("(ERROR) Unable to load application settings")
        sys.exit(2)

    try:
        from simple_settings import settings

        app_name = settings.APP_NAME

        print(f"Simple settings are correctly loaded - AppName: {app_name}")
    except ImportError as err:
        print(err)
        print("(ERROR) Simple settings library has issue loading settings")
        sys.exit(3)


def print_run_data():
    from simple_settings import settings

    print("*" * 80)
    print("* SETTINGS: {}".format(os.environ['SIMPLE_SETTINGS']))
    print("* APP_NAME: {}".format(settings.APP_NAME))
    print("* ENV: {}".format(settings.ENV))
    print("* HOST (PORT): http://{}:{}/".format(
        settings.FLASK_SERVER_HOST, settings.FLASK_SERVER_PORT))
    print("* DEBUG: {}".format(settings.DEBUG))
    print("* FACTORY: {}".format(os.environ['FLASK_APP']))
    print("*" * 80)


def main(as_module=False):
    print("Checking environmental variables")

    print("")

    check_variables()

    print("")

    print("Checking availability of settings")

    print("")

    check_settings()

    print("")

    print_run_data()

    print("")

    flask_main(as_module)


if __name__ == '__main__':
    main(True)
