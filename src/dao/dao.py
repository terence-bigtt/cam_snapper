class DirectoryException(Exception):
    def __init__(self):
        Exception.__init__(self, "Directory not initialized")


class FileDaoException(Exception):
    def __init__(self, cause=None):
        if cause:
            message = str(cause.args)
        else:
            message = ""
        Exception.__init__(self, "Couldn't perform operation because of {}".format(message))


class Dao(object):
    dao_type = None

    def write(self, path, content): pass

    def read(self, path): pass
