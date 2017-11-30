import os
import datetime
import time


class Storage:
    def __init__(self, storage_config):
        self._storage_base = storage_config.get("base", ".")
        self._snap_folder = storage_config.get("snaps", dict()).get('folder', 'snaps')
        self._archive_folder_format = storage_config.get('archive', {}).get('format', 'Y-%m-%d')
        self._archive_folder = storage_config.get("archive", dict()).get('folder', 'archive')

        self.snap_path = self._get_snap_path()
        self.archive_base_path = self._get_base_archive_path()
        self.snap_storage_timeout = Storage._get_snap_storage_timeout(storage_config)

    @staticmethod
    def _get_snap_storage_timeout(store_config):
        snap_conf = store_config.get("snaps") or dict()
        timeout = snap_conf.get("timeout")
        if timeout is None:
            return
        unit = snap_conf.get("unit")
        factor = 1
        if unit == "minute":
            factor = 60
        elif unit == "hour":
            factor = 60 * 60
        elif unit == "day":
            factor = 24 * 60 * 60
        elif unit == "week":
            factor = 7 * 24 * 60 * 60
        return timeout * factor

    def _get_snap_path(self):
        return os.path.join(self._storage_base, self._snap_folder)

    def _get_base_archive_path(self):
        return os.path.join(self._storage_base, self._archive_folder)

    def _get_archive_path(self, created_at=None):
        creation_date = datetime.datetime.fromtimestamp(created_at or time.time())
        archive_folder = creation_date.strftime(self._archive_folder_format)
        base_path = self.archive_base_path
        return os.path.join(base_path, archive_folder)

    def get_cam_snap_path(self, cam_name):
        return os.path.join(self.snap_path, cam_name)

    def get_cam_archive_path(self, cam_name, created_at):
        return os.path.join(self._get_archive_path(created_at), cam_name)

    def get_cam_storage_path(self, cam_name, created_at=None):
        snaps = os.path.join(self.snap_path, cam_name)
        archive = os.path.join(self._get_archive_path(created_at), cam_name)
        return snaps, archive
