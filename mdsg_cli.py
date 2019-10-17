
from utils.command_parser import CommandParser
from utils.custom_logging import message
from utils.custom_logging import Logging
from generator.digit_sequence_generator import DigitSequenceGenerator
import json

logger = Logging(__name__).get_logger()

if __name__ == "__main__":
    """
        Start of the program
        :args: cli : Eg : python mdsg_cli.py -d 3 5 0 -sr1 4 -sr2 8 -w 130
        :return: Image
    """
    try:
        """
        Parse the command line arguments
        """
        command_parser = CommandParser()
        arguments = command_parser.cli_argument_parser()

        """
        Logger start
        """
        logger.info('Program execution start')
        message('Program execution start')

        """
        Start the sequence generator
        """
        generator = DigitSequenceGenerator(arguments)
        generator.generate_numbers_sequence()

        """
        Save the generated image sequence
        """
        img_file_name = generator.image_downloader()

        if len(img_file_name):
            # generator.log_info(img_file_name)
            outputData = generator.image_info
            outputData["filename"] = img_file_name[0]
            logger.info('Execution successful : Output : {}'.format(outputData))
            message('Execution successful : Output : {}'.format(outputData))

        else:
            logger.error('Execution fail')
            message('Execution fail : check logs')
    except Exception as e:
        logger.error('Failed to execute program : Exception : {}'.format(e))
        message("Failed to execute program : Exception : {}".format(e))
        exit(1)
