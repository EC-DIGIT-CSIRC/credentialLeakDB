from lib.helpers import getlogger


logger = getlogger(__name__)


class Foo:
    def __init__(self):
        pass

    def do_smthg(self):
        logger.info("bar")
        print("baz")


def test_logger():
    logger.info("starting up the class")

    f = Foo()
    f.do_smthg()
    logger.info("DONE")
    assert True


if __name__ == "__main__":
    test_logger()
