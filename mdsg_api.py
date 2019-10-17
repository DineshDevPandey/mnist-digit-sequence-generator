# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_restful import Resource, Api, output_json

from utils.command_parser import CommandParser, logger
from generator.digit_sequence_generator import DigitSequenceGenerator
from utils.custom_logging import message

app = Flask(__name__)
api = Api(app)


class MDSG(Resource):
    def get(self):

        """
        Logger start
        """
        logger.info('Program execution start')
        message('Program execution start')

        """
        Parse the command line arguments
        """
        command_parser = CommandParser()
        go, arguments = command_parser.api_argument_parser()

        if go:
            try:
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
                    return('Execution successful : Output : {}'.format(outputData))

                else:
                    logger.error('Execution fail')
                    return('Execution fail : check logs')
            except Exception as e:
                logger.error('Failed to execute program : Exception : {}'.format(e))
                return("Failed to execute program : Exception : {}".format(e))
                exit(1)


api.add_resource(MDSG, '/mdsg')  # Route_1

if __name__ == '__main__':
    app.run()
    # http://127.0.0.1:5000/mdsg?d=4&d=5&d=8&sr1=3&sr2=9&w=100