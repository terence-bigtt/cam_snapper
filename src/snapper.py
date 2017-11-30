from archiver import Archiver
from cam_snapper import IpCamSnapper
from dao.file import FileDao
import os


class Snapper:
    def __init__(self, cam_config, storage):
        self.storage = storage
        self.cam = IpCamSnapper(cam_config)
        self.writer = FileDao()
        self.archiver = Archiver(self.storage, self.cam)
        self.store_in = self.storage.get_cam_snap_path(self.cam.name)

    def snap(self):
        snap = None
        try:
            snap = self.cam.snap()
        except Exception as e:
            print(e.args)
            print("exception in snap")
            # TODO: log exception

        if snap:
            filename = snap.name + os.extsep + self.cam.ext
            self.writer.set_directory(self.store_in).write(filename, snap.content)

    def archive(self):
        self.archiver.archive()
