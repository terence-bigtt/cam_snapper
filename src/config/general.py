import yaml

from config.ip_cam import IpCam
from config.storage import Storage


class GeneralConfig:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            config_content = "\n".join(f.readlines())
            settings = yaml.load(config_content)

        self._storage_settings = settings.get("storage", {})
        self._cam_settings = settings.get("cam", {})
        self.storage = Storage(self._storage_settings)
        self.cams = [IpCam(cam_setting) for cam_setting in self._cam_settings]
        self.snap_every = settings.get('snap_every', 10)
