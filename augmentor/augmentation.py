from utils.config_parser import ConfParser
import augmentor.operations as ops


class Augmentor(object):
    def __init__(self, img_array):
        self.img_array = img_array
        self._parser = ConfParser().parser
        self._rand_aug = self._parser.get('AUGMENTATION', 'RandAug')
        self._rotate = self._parser.get('AUGMENTATION', 'Rotate')
        self._blur = self._parser.get('AUGMENTATION', 'Blur')
        self._warp = self._parser.get('AUGMENTATION', 'Warp')
        self._verticalflip = self._parser.get('AUGMENTATION', 'VerticalFlip')
        self._horizontalflip = self._parser.get('AUGMENTATION', 'HorizontalFlip')

    def execute(self):
        if self._rotate:
            rotate = ops.Rotate(self.img_array)
            rotated_img = rotate.execute()
            return rotated_img

        if self._blur:
            blur = ops.Blur(self.img_array)
            blured_img = blur.execute()
            return blured_img

        if self._warp:
            warp = ops.Warp(self.img_array)
            warped_img = warp.execute()
            return warped_img

        if self._verticalflip:
            verticalflip = ops.Verticalflip(self.img_array)
            verticalfliped_img = verticalflip.execute()
            return verticalfliped_img

        if self._horizontalflip:
            horizontalflip = ops.Horizontalflip(self.img_array)
            horizontalfliped_img = horizontalflip.execute()
            return horizontalfliped_img



