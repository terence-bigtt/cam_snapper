import numpy as np
from PIL import Image
import io


class MotionDetector:
    def __init__(self, threshold=5, sensitivity=0.01, channel=1):
        """
        Class for motion detection using differential background method

        :param threshold: pixel value difference for asserting a pixel change
        :param sensitivity: ammount of pixel that has changed for asserting a motion
        :param channel: 0,1,2 or None, which channel to check motion on
        :return:
        """
        self.threshold = threshold
        self.channel = channel
        self.sensitivity = sensitivity
        self.thresholdfunction = self._make_thresholdfunction(threshold)

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.thresholdfunction = self._make_thresholdfunction(threshold)
        return self

    def set_sensitivity(self, sensitivity):
        self.sensitivity = sensitivity
        return self

    def _make_thresholdfunction(self, thre):
        def applythreshold(v):
            return int(v > thre)

        return np.vectorize(applythreshold)

    def has_moved(self, im, *bg):
        """

        :param im: image to check, PIL object
        :param bg: images for the background. PIL objects
        :return: Boolean if motion is detected
        """
        return self.detect_motion(im, *bg)[0]

    def has_moved_frombytes(self, im, *imbg):
        image = self._load_from_bytes(im)
        imagesbgs = map(self._load_from_bytes, imbg)
        return self.has_moved(image, *imagesbgs)

    def get_movement(self, im, *bg):
        """

        :param im: image to check, PIL object
        :param bg: images for the background. PIL objects
        :return: differential image (np.array shaped resx x resy x 3)
        """
        return self.detect_motion(im, *bg)[-1]

    def get_movement_frombytes(self, im, *imbg):
        image = self._load_from_bytes(im)
        imagesbgs = map(self._load_from_bytes, imbg)
        return self.get_movement(image, *imagesbgs)

    def detect_motion(self, im, *imbg):
        """

        :param im: image to check, PIL object
        :param bg: images for the background. PIL objects
        :return:
            -boolean for motion detection,
            np.array of
            - image to check,
            - mean background,
            - absolute difference
            - array of (absolute difference > thresold)
        """
        channels1 = self.reshapemultichannel(np.asarray(im)[:, :, self.channel].astype(int))
        channelsbg = [self.reshapemultichannel(np.asarray(im)[:, :, self.channel].astype(int)) for im in imbg]
        channels2 = channelsbg[0]
        for ch in channelsbg[1:]:
            channels2 = channels2 + ch
        channels2 /= len(channelsbg)
        delta = (channels2 - channels1)
        tdelta = self.thresholdfunction(delta)
        variationamount = tdelta.sum() / float(np.product(tdelta.shape[:2]))
        motion = variationamount > self.sensitivity
        return motion, channels1, channels2, delta, tdelta

    def detect_motion_frombytes(self, im, *imbg):
        image = self._load_from_bytes(im)
        imagesbgs = map(self._load_from_bytes, imbg)
        return self.detect_motion(image, *imagesbgs)

    @staticmethod
    def _load_from_bytes(data):
        return Image.open(io.BytesIO(data))

    @staticmethod
    def reshapemultichannel(im):
        return im.reshape([s for s in im.shape if s != 1])
