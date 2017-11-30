import os

from src.dao.dao import Dao, DirectoryException


class FileDao(Dao):
    directory_exception = DirectoryException

    def __init__(self, directory_path=None):
        Dao.__init__(self)
        self.dao_type = 'file'
        self.path = directory_path

    def set_directory(self, path):
        self.path = path
        return self

    def read(self, name):
        if self.path is None: raise self.directory_exception
        try:
            with open(os.path.join(self.path, name), 'r') as f:
                return ''.join(f.readlines())
        except Exception as e:
            raise Exception("couldn't read file {} because of {}".format(name, e.message))

    def write(self, name, content):
        if self.path is None: raise self.directory_exception
        try:
            self.mkdir_recursive(self.path)
            with open(os.path.join(self.path, name), 'wb') as f:
                f.write(content)
        except Exception as e:
            raise Exception("couldn't read file {} because of {}".format(name, e.message))

    @staticmethod
    def split_path(path_to_split):
        path, folder = os.path.split(path_to_split)
        folders = [folder]
        while 1:
            path, folder = os.path.split(path)

            if folder != "":
                folders.append(folder)
            else:
                if path != "":
                    folders.append(path)

                break

        folders.reverse()
        return folders

    @staticmethod
    def mkdir_recursive(path):
        split = FileDao.split_path(path)
        for i, folder in enumerate(split):
            current = os.path.join(*split[:i + 1])
            if not os.path.exists(current):
                os.mkdir(current)
        return True
