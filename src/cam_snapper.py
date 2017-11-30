import time
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth


class Snap:
    def __init__(self, content, created_at=None, name=None):
        self.content = content
        self.created_at = created_at or time.time()
        self.name = name or str(self.created_at)


class IpCamSnapper:
    def __init__(self, cam):
        """
        Initializes an interface to IpCam from a IpCam object
        :param cam: IpCam object
        :return: IpCamSnapper
        """
        self.name, self.url, self.auth, self.ext = cam.name, cam.url, cam.auth, cam.ext

    def snap(self):
        """
        gets a snap from  the cam
        :return: Snap object
        """
        req = requests.get(self.url, auth=self.auth, timeout=1)
        content = req.content
        return Snap(content)
