import os
import shutil
import time, datetime

# TODO
# Refactor here
# Create a archiveHandler
from dao.file import FileDao


class Archiver:
    def __init__(self, storage, cam):
        self.storage = storage
        self.cam = cam
        self.timeout = storage.snap_storage_timeout
        self.mkdir_recursive = FileDao.mkdir_recursive

    def set_timeout(self, timeout):
        self.timeout = timeout
        return self

    def archive(self):
        cam = self.cam
        snappath = self.storage.get_cam_snap_path(cam.name)
        old_files = self._get_old_files(snappath, self.timeout)
        creation_times = {f: os.path.getctime(f) for f in old_files}
        for f in creation_times.keys():
            destination = self.storage.get_cam_storage_path(cam.name, creation_times[f])
            self._move_file(f, destination[1])

    @staticmethod
    def _move_file(srcfile, destination):
        destinationdirectory = Archiver.getdirname(destination)
        if Archiver.isfilepath(destination):
            filename = os.path.basename(destination)
        else :
            filename = os.path.split(srcfile)[-1]
        FileDao.mkdir_recursive(destination)
        destfile = os.path.join(destinationdirectory, filename)
        shutil.move(srcfile, destfile)

    @staticmethod
    def getdirname(destination):
        if Archiver.isfilepath(destination):
            return os.path.join(*[p for p in os.path.split(destination) if p][:-1] or [os.curdir])
        else :
            return destination

    @staticmethod
    def isfilepath(path):
        return len([el for el in os.path.basename(path).split(os.path.extsep) if el])>1

    @staticmethod
    def _get_creation_times(path):
        listdir = os.listdir(path)
        listfiles = map(lambda f: os.path.join(path, f), listdir)
        files = {f: os.path.getctime(f) for f in listfiles if os.path.isfile(f)}
        return files

    @staticmethod
    def _get_ages(path):
        now = time.time()
        files = Archiver._get_creation_times(path)
        ages = {f: now - files.get(f) for f in files.keys()}
        return ages

    @staticmethod
    def _get_old_files(path, timeout):
        ages = Archiver._get_ages(path)
        return [f for f in ages.keys() if ages.get(f) > timeout]
