import math
import re
import os
import json
import traceback
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from utils.custom_logging import Logging
from utils.config_parser import ConfParser
from augmentor.augmentation import Augmentor
from generator.image_data_reader import ImageDataReader

logger = Logging(__name__).get_logger()


class DigitSequenceGenerator(object):
    def __init__(self, cmd_args):
        try:
            self.config = ConfParser()

            self.digits = cmd_args["digits"]
            self.spacing_range_max = cmd_args["maxSpacingRange"]
            self.spacing_range_min = cmd_args["minSpacingRange"]
            self.image_width = cmd_args["imageWidth"]

            input_dir = os.path.join(os.path.dirname(__file__), '../input_data/')
            output_dir = os.path.join(os.path.dirname(__file__), '../')

            self.image_file = os.path.join(input_dir, self.config.parser.get('GENERATOR', 'ImagePath'))
            self.image_label_file = os.path.join(input_dir, self.config.parser.get('GENERATOR', 'LabelPath'))
            self.output_path = os.path.join(output_dir, self.config.parser.get('GENERATOR', 'OutputPath'))
            self.spacing_mode = self.config.parser.get('GENERATOR', 'spacingMode')
            self.white_pixel = self.config.parser.get('GENERATOR', 'whitePixel')

            self._mdsg_mode = int(self.config.parser.get('AUGMENTATION', 'mdsg_mode'))

            self._img_map = None
            self.image_info = None
            self.aug_image_info = None
            self._random_img_array = None
            self._aug_random_img_array = None
            self.output_image_array = None
            self.aug_output_image_array = None

            self.img_reader = ImageDataReader(self.image_file, self.image_label_file)

        except Exception as e:
            logger.error("Unable to build DigitSequenceGenerator Object, exception : {}".format(str(e)))
            logger.exception(e)
            raise e

    def generate_numbers_sequence(self):
        """
        Function to generate sequence
        :return:
        """
        try:
            self._img_map = self.img_reader.read_image()
        except Exception as e:
            logger.error("Image data read fail : Exception : {}".format(e))
            logger.error(
                "\n".join([line.rstrip('\n') for line in traceback.format_exception(e.__class__, e, e.__traceback__)]))
            raise e

        try:
            self._random_img_array = self._select_images()
            # for augmented and compare mode
            if self._mdsg_mode == 2 or self._mdsg_mode == 3:
                self._aug_random_img_array = Augmentor(self._random_img_array).execute()
                self.aug_output_image_array, self.aug_image_info = self._generate_sequence(mode='augment')

            # for original and compare mode
            if self._mdsg_mode == 1 or self._mdsg_mode == 3:
                self.output_image_array, self.image_info = self._generate_sequence(mode='original')

        except Exception as e:
            logger.error("Image sequence generator fail, Exception : {}".format(e))
            logger.error(
                "\n".join([line.rstrip('\n') for line in traceback.format_exception(e.__class__, e, e.__traceback__)]))
            raise e

    def _select_images(self):
        """
        Select a random image from pool of images as per user input
        :return: list of images
        """
        try:
            # We should make a list of rawImages so that the order of input given in digits can be maintained #
            rawImageList = list()
            logger.info("User input digit list = {}".format(str(self.digits)))
            for user_digit in self.digits:
                if str(user_digit) in self._img_map.keys():
                    images_for_digit = self._img_map[str(user_digit)]
                    chosen_image_idx = np.random.choice(np.arange(0, images_for_digit.shape[0]), 1, replace=False)
                    chosen_image = images_for_digit[chosen_image_idx, :, :]
                    chosen_image = chosen_image.reshape(chosen_image.shape[1], chosen_image.shape[2])
                    logger.debug(
                        "For user input digit = {}, chosen index from in-memory dict = {}".format(str(user_digit),
                                                                                                  chosen_image_idx))
                    rawImageList.append(chosen_image)
                else:
                    error = "user provided digit = {}, not present in image data base. Unique image labels are : {}".format(
                        str(user_digit), str(self._img_map.keys()))
                    logger.error(error)
                    raise (Exception(error))
            return rawImageList
        except Exception as e:
            raise (e)

    def image_downloader(self):
        """
        Function for downloading the output image based on mdsg_mode flag.
        mode 1: original image only
        mode 2: augmented image only
        mode 3: both
        :return: Image file list
        """

        iteration = math.ceil(self._mdsg_mode / 2.0)
        file_name = list()

        for itr in range(iteration):
            """
            For original image mode and both mode's first iteration (original image) 
            """
            if self._mdsg_mode == 1 or (self._mdsg_mode == 3 and itr == 0):
                image_array = self.output_image_array
                image_info = self.image_info
                _ext = 'org'

            """
            For augmented image mode and both mode's first iteration (augmented image) 
            """
            if self._mdsg_mode == 2 or (self._mdsg_mode == 3 and itr == 1):
                image_array = self.aug_output_image_array
                image_info = self.aug_image_info
                _ext = 'aug'

            """
            Save image in png format. 
            for original image suffix : _ord_
            for augmented image suffix : _aug_
            """
            try:
                filename = os.path.realpath(
                    self.output_path + "/mdsg_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S_") + _ext + "_" +
                    image_info["fullImageSize"].strip("(").strip(")").replace(", ", "x") + ".png")
                logger.info("Writing image to output file = {}".format(filename))
                plt.imsave(fname=filename, arr=np.float32(image_array), cmap="gray")
                file_name.append(filename)

            except Exception as e:
                logger.error(
                    "Unable to save image, size = {}, filename = {}, exception = {}".format(image_info["fullImageSize"],
                                                                                            filename, str(e)))
                return False

        return file_name

    def _generate_sequence(self, mode='original'):

        if mode == 'augment':
            _img_array = self._aug_random_img_array
        else:
            _img_array = self._random_img_array

        try:
            # minimum space calculation
            minRequiredWidth = sum([x.shape[1] for x in _img_array])
            if minRequiredWidth > self.image_width:
                error = "User input image width = {} is (less than) sum of width of selected images = {}.".format(
                    self.image_width, minRequiredWidth)
                logger.error(error)
                raise (Exception(error))

            # For equalized spacing
            if (re.search("^(EQUALIZED){1}_{1}(MAX|MIN)$", self.spacing_mode)):

                rightEndWhiteSpaceLeft = self.image_width - (minRequiredWidth + (
                            (len(_img_array) - 1) * np.arange(self.spacing_range_min, self.spacing_range_max + 1, 1)))
                if not len(np.where(rightEndWhiteSpaceLeft >= 0)[0]) > 0:
                    error = "For spacing_mode = {},\
                    with min spacing_range = {} and\
                    max spacing range = {},\
                    image_width = {} and\
                    totalWidthOfAllImages = {}, fitting is not possible.\n\
                    RightEndSpacingLeft = {}".format(self.spacing_mode,
                                                     self.spacing_range_min,
                                                     self.spacing_range_max,
                                                     self.image_width,
                                                     minRequiredWidth,
                                                     str(rightEndWhiteSpaceLeft))
                    logger.error(error)
                    raise (Exception(error))

                if (self.spacing_mode == "EQUALIZED_MAX"):
                    equalized_min_max_func = min
                else:
                    equalized_min_max_func = max

                logger.debug("User selected spacing mode = {}".format(self.spacing_mode))

                # distance between two images
                selectedBetweenSpace = (np.arange(self.spacing_range_min, self.spacing_range_max + 1, 1)[np.where(
                    rightEndWhiteSpaceLeft == equalized_min_max_func(
                        rightEndWhiteSpaceLeft[np.where(rightEndWhiteSpaceLeft >= 0)]))])[0]
                leftSpace = int(
                    equalized_min_max_func(rightEndWhiteSpaceLeft[np.where(rightEndWhiteSpaceLeft >= 0)]) / 2)
                rightSpace = equalized_min_max_func(
                    rightEndWhiteSpaceLeft[np.where(rightEndWhiteSpaceLeft >= 0)]) - leftSpace

                if ((leftSpace + minRequiredWidth + (
                        selectedBetweenSpace * (len(_img_array) - 1)) + rightSpace) != self.image_width):
                    error = "FATAL ERROR : user image width = {}, betweenspace = {}, leftspace = {}, rightspace = {}, SUMMATION DOES NOT MATCH, CHECK LOGS".format(
                        self.image_width, selectedBetweenSpace, leftSpace, rightSpace)
                    logger.error(error)
                    raise (Exception(error))

                maxHeightAmongAllImages = max([x.shape[0] for x in _img_array])
                logger.debug(
                    "betweenspace = {}, leftspace = {}, rightspace = {}, maxheight = {}".format(selectedBetweenSpace,
                                                                                                leftSpace, rightSpace,
                                                                                                maxHeightAmongAllImages))

                selectedBetweenSpaceArray = np.repeat(self.white_pixel,
                                                      (maxHeightAmongAllImages * selectedBetweenSpace)).reshape(
                    maxHeightAmongAllImages, selectedBetweenSpace)
                leftSpaceArray = np.repeat(self.white_pixel, (maxHeightAmongAllImages * leftSpace)).reshape(
                    maxHeightAmongAllImages, leftSpace)
                rightSpaceArray = np.repeat(self.white_pixel, (maxHeightAmongAllImages * rightSpace)).reshape(
                    maxHeightAmongAllImages, rightSpace)

                logger.debug("\n\
                selectedBetweenSpace = {}\n\
                leftSpace = {}\n\
                rightSpace = {}\n\
                maxHeightAmongAllImages = {}\n\
                selectedBetweenSpaceArray.shape = {}\n\
                leftSpaceArray.shape = {}\n\
                rightSpaceArray.shape = {}\n\
                rightEndWhiteSpaceLeft.shape = {}\n\
                rightEndWhiteSpaceLeft (array) = {}".format(selectedBetweenSpace, leftSpace, rightSpace,
                                                            maxHeightAmongAllImages,
                                                            str(selectedBetweenSpaceArray.shape),
                                                            str(leftSpaceArray.shape), str(rightSpaceArray.shape),
                                                            str(rightEndWhiteSpaceLeft.shape),
                                                            str(rightEndWhiteSpaceLeft)))


                finalImage = _img_array[0]
                for image in _img_array[1:]:
                    logger.debug("finalImage before white space addition = {}".format(str(finalImage.shape)))
                    finalImage = np.hstack((finalImage, selectedBetweenSpaceArray, image))
                    logger.debug("finalImage after white space addition = {}".format(str(finalImage.shape)))

                finalImage = np.hstack((leftSpaceArray, finalImage, rightSpaceArray))

                imageMetaInfo = dict()
                imageMetaInfo["fullImageSize"] = str((maxHeightAmongAllImages, leftSpace + minRequiredWidth + (
                            selectedBetweenSpace * (len(_img_array) - 1)) + rightSpace))
                imageMetaInfo["leftMargin"] = str(leftSpace)
                imageMetaInfo["rightMargin"] = str(rightSpace)
                imageMetaInfo["betweenMargins"] = str(np.repeat(selectedBetweenSpace, len(_img_array)))
                imageMetaInfo["numberOfLabels"] = str(len(_img_array))

                logger.debug("finalImage FINALLY = {}".format(str(finalImage.shape)))
                logger.info("FINAL PROCESSED IMAGE METAINFO :\n{}".format(json.dumps(imageMetaInfo, indent=2)))
            else:
                # Processing for PROGRESSIVE MODE #
                selectedBetweenSpace = np.arange(self.spacing_range_min, self.spacing_range_max + 1, 1)[
                                       0:len(_img_array) - 1]
                rightEndWhiteSpaceLeft = self.image_width - (minRequiredWidth + sum(selectedBetweenSpace))
                if (rightEndWhiteSpaceLeft < 0):
                    error = "For spacing_mode = {}, with min spacing_range = {} and max spacing range = {},image_width = {} and totalWidthOfAllImages = {},selectedBetweenSpace = {} fitting is not possible.\nRightEndSpacingLeft = {}".format(
                        self.spacing_mode,
                        self.spacing_range_min,
                        self.spacing_range_max,
                        self.image_width,
                        minRequiredWidth,
                        str(selectedBetweenSpace),
                        rightEndWhiteSpaceLeft)
                    logger.error(error)
                    raise (Exception(error))

                leftSpace = int(rightEndWhiteSpaceLeft / 2)
                rightSpace = rightEndWhiteSpaceLeft - leftSpace

                if ((leftSpace + minRequiredWidth + sum(selectedBetweenSpace) + rightSpace) != self.image_width):
                    error = "FATAL ERROR : user image width = {}, betweenspace = {}, leftspace = {}, rightspace = {}, SUMMATION DOES NOT MATCH, CHECK LOGS".format(
                        self.image_width, selectedBetweenSpace, leftSpace, rightSpace)
                    logger.error(error)
                    raise (Exception(error))

                maxHeightAmongAllImages = max([x.shape[0] for x in _img_array])

                logger.debug("betweenspace = {}, leftspace = {}, rightspace = {}, maxheight = {}".format(
                    str(selectedBetweenSpace), leftSpace, rightSpace, maxHeightAmongAllImages))

                leftSpaceArray = np.repeat(self.white_pixel, (maxHeightAmongAllImages * leftSpace)).reshape(
                    maxHeightAmongAllImages, leftSpace)
                rightSpaceArray = np.repeat(self.white_pixel, (maxHeightAmongAllImages * rightSpace)).reshape(
                    maxHeightAmongAllImages, rightSpace)

                finalImage = _img_array[0]
                for itr in np.arange(1, len(_img_array), 1):
                    logger.debug("finalImage before white space addition = {}".format(str(finalImage.shape)))
                    selectedBetweenSpaceArray = np.repeat(self.white_pixel,
                                                          maxHeightAmongAllImages * selectedBetweenSpace[
                                                              itr - 1]).reshape(maxHeightAmongAllImages,
                                                                                selectedBetweenSpace[itr - 1])
                    image = _img_array[itr]
                    finalImage = np.hstack((finalImage, selectedBetweenSpaceArray, image))
                    logger.debug("finalImage after white space addition = {}".format(str(finalImage.shape)))

                finalImage = np.hstack((leftSpaceArray, finalImage, rightSpaceArray))

                imageMetaInfo = dict()
                imageMetaInfo["fullImageSize"] = str(
                    (maxHeightAmongAllImages, leftSpace + minRequiredWidth + sum(selectedBetweenSpace) + rightSpace))
                imageMetaInfo["leftMargin"] = str(leftSpace)
                imageMetaInfo["rightMargin"] = str(rightSpace)
                imageMetaInfo["betweenMargins"] = str(selectedBetweenSpace)
                imageMetaInfo["numberOfLabels"] = str(len(_img_array))

                logger.debug("finalImage FINALLY = {}".format(str(finalImage.shape)))
                logger.info("FINAL PROCESSED IMAGE METAINFO :\n{}".format(json.dumps(imageMetaInfo, indent=2)))

            return finalImage, imageMetaInfo

        except Exception as e:
            raise e

