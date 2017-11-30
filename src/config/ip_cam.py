import time
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth


class IpCam:
    def __init__(self, cam_settings):
        """
        Parses cam settings
        :param cam_settings: configuration dictionnary
        :return: IpCam
        """
        self.name, self.url, self.auth, self.ext = self._parse_cam_settings(cam_settings)


    @staticmethod
    def _parse_cam_settings(cam_settings):
        name = cam_settings.get("name", cam_settings["url"])
        auth_type = cam_settings.get("auth_type")
        if auth_type == "DIGEST":
            auth = HTTPDigestAuth(cam_settings['user'], cam_settings['password'])
        elif auth_type == "BASIC":
            auth = HTTPBasicAuth(cam_settings['user'], cam_settings['password'])
        else:
            auth = None

        url = cam_settings['url']

        extension = cam_settings.get("format") or 'jpg'
        return name, url, auth, extension
