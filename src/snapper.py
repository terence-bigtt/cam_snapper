from archiver import Archiver
from cam_snapper import IpCamSnapper
from dao.file import FileDao
import os

class Snapper:
    def __init__(self, general_config):
        self.general = general_config
        self.cams = [IpCamSnapper(c) for  c in general_config.cams]
        self.writer = FileDao()
        self.archivers = [Archiver(self.general.storage, cam) for cam in self.cams]

    def snap(self):
        snaps = {}
        for c in self.cams:
            try:
                snaps.update({c: c.snap()})
            except Exception as e:
                print(e.args)
                print("exception in snap")
                # TODO: log exception
            snap = snaps.get(c)
            if snap:
                store_in = self.general.storage.get_cam_snap_path(c.name)
                filename = snap.name + os.extsep + c.ext
                self.writer.set_directory(store_in).write(filename, snap.content)

    def archive(self):
        for archiver in self.archivers:
            archiver.archive()
