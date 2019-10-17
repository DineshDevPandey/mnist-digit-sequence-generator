import random
import numpy as np
from skimage.transform import rotate, warp, SimilarityTransform
from skimage.util import random_noise
from scipy import ndimage
from utils.config_parser import ConfParser

class Rotate(object):

    def __init__(self, in_img):
        self._parser = ConfParser().parser
        self.max_left_degree = int(self._parser.get('AUGMENTATION', 'max_left_degree'))
        self.max_right_degree = int(self._parser.get('AUGMENTATION', 'max_right_degree'))
        self.in_img = in_img
        self.out_img = list()

    def execute(self):
        for index in range(len(self.in_img)):
            random_degree = random.uniform(-self.max_right_degree, self.max_left_degree)
            self.out_img.append(rotate(image=self.in_img[index], angle=random_degree, mode='wrap'))

        return self.out_img


class RandomNoise(object):

    def __init__(self, in_img):
        self.in_img = in_img
        self.out_img = list()

    def execute(self):
        for index in range(len(self.in_img)):
            self.out_img.append(random_noise(image=self.in_img[index]))

        return self.out_img


class Blur(object):

    def __init__(self, in_img):
        self.in_img = in_img
        self.out_img = list()

    def execute(self):
        for index in range(len(self.in_img)):
            self.out_img.append(ndimage.uniform_filter(input=self.in_img[index]))

        return self.out_img


"""
Not applicable for some digits 1, 2, 3, 5, 7, 9 
"""
class HorizontalFlip(object):

    def __init__(self, in_img):
        self.in_img = in_img
        self.out_img = list()

    def execute(self):
        for index in range(len(self.in_img)):
            self.out_img.append(self.in_img[index][:, ::-1])

        return self.out_img


"""
Not applicable for some digits 
"""
class VerticalFlip(object):

    def __init__(self, in_img):
        self.in_img = in_img
        self.out_img = list()

    def execute(self):
        for index in range(len(self.in_img)):
            self.out_img.append(self.in_img[index][:, ::-1][::-1, :])

        return self.out_img


class Warp(object):

    def __init__(self, in_img):
        self.matrix = np.array([[1, 0, 0], [0, 1, -10], [0, 0, 1]])
        self.in_img = in_img
        self.out_img = list()

    def execute(self):
        for index in range(len(self.in_img)):
            tform = SimilarityTransform(translation=(0, 4))
            self.out_img.append(warp(self.in_img[index], inverse_map=tform, clip=True, mode='wrap'))

        return self.out_img


