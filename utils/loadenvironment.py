from os.path import join, dirname

from dotenv import load_dotenv


def load_environment(debug: bool = False, override: bool = False):
    """
    Get the environment variables loaded into memory
    """
    dotenv_path = join(dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path, debug, override)


def load_test_environment(debug: bool = True, override: bool = False):
    """Get the environment variables for testing"""
    dotenv_path = join(dirname(__file__), '..', 'test.env')
    load_dotenv(dotenv_path, debug, override)
