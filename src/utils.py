import sys


# ......................................................................................................................
def decode(path: str) -> str:
    """
    utility fct to encode/decode
    """
    return path.encode(sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)


# ......................................................................................................................
class TestError:
    """
    Class to store error
    """

    def __init__(self, error):
        """
        Test Error Class
        """
        self.type = error.__class__.__name__ if isinstance(error, Exception) else 'Error'
        self.message = str(error)

    def __str__(self):
        return '[%s: %s]' % (self.type, self.message)
