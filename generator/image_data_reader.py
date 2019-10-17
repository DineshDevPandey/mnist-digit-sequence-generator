import struct
import numpy as np
from array import array
from utils.custom_logging import Logging

logger = Logging(__name__).get_logger()


class ImageDataReader(object):
    """
    Read image data, normalize it and create a dict of label and images
    """
    def __init__(self, image_file, imageLabelFile):
        try:
            self.image_file = image_file
            self.imageLabelFile = imageLabelFile
        except Exception as e:
            logger.error("Unable to create object for ImageDataReader class, exception : {}".format(str(e)))
            raise e

    def read_image(self):
        try:
            return self.__read_image()
        except Exception as e:
            logger.error("Unable to read image data, imageFile = {} & imageLabelFile = {} & exception : {}".format(
            str(self.image_file), str(self.imageLabelFile), str(e)))
            raise e

    def __read_image(self):
        try:
            with open(self.image_file, "rb") as f:
                magic_num, size, rows, cols = struct.unpack(">IIII", f.read(16))
                logger.info(
                    "imageFile -> magic_num = {}, size = {}, rows = {}, cols = {}".format(magic_num, size, rows, cols))
                if magic_num != 2051:
                    error = "While reading image data, magic number not as expceted. Expected value = 2051, value received = {}".format(
                        magic_num)
                    logger.error(error)
                    raise (Exception(error))
                image = list(map(lambda px: (255 - px) / 255.0, array("B", f.read())))
                parsed_images = np.asarray(image, dtype=np.float32).reshape(size, rows, cols)
            logger.info("Completed parsing imageFile, number of images read = {}".format(parsed_images.shape[0]))


            with open(self.imageLabelFile, "rb") as f:
                magic_num, size = struct.unpack(">II", f.read(8))
                logger.info("imageLabelFile -> magic_num = {}, size = {}".format(magic_num, size))
                if magic_num != 2049:
                    error = "While reading image label data, magic number not as expected. Excepted value = 2049, value received = {}".format(
                        magic_num)
                    logger.error(error)
                    raise (Exception(error))
                parsed_labels = np.array(array("B", f.read())).reshape(size, 1)
            logger.info("Completed parsing imageLabelFile, number of labels parsed = {}, unique lables = {}".format(
            parsed_labels.shape[0], str(np.unique(parsed_labels))))

            # Build the final dict #
            img_map = dict()
            for label in np.unique(parsed_labels):
                img_map[str(label)] = parsed_images[np.where(label == parsed_labels)[0], :, :]
            logger.info(
                "For unique image labels as {}, the number of images found = {} totalling = {} images in the dict".format(
                str(np.unique(parsed_labels)),
                str([img_map[str(x)].shape[0] for x in np.unique(parsed_labels)]),
                sum([img_map[str(x)].shape[0] for x in np.unique(parsed_labels)])))
            return img_map

        except Exception as e:
            raise e
