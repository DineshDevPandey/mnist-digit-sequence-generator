import sys
import json
import argparse

from flask import jsonify
from flask_restful import reqparse
from utils.custom_logging import Logging, message

logger = Logging(__name__).get_logger()


class CommandParser(object):
    def __init__(self):
        pass

    def cli_argument_parser(self):
        '''
        Command line argument parsing function
        :return:
        '''

        try:
            parser = argparse.ArgumentParser(prog='mdsg_cli', description='Digit sequence generator using mnist')

            parser.add_argument('-d',
                                '--digits',
                                dest='digits',
                                nargs="+",
                                type=int,
                                choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                                required=True,
                                help='space separated digits to generate : Eg: -d 3 8 1')

            parser.add_argument('-sr1',
                                '--min_sr',
                                dest='minSpacingRange',
                                type=int,
                                required=True,
                                help="min of spacing range : Eg: -sr1 30 (in pixels)")

            parser.add_argument('-sr2',
                                '--max_sr',
                                dest='maxSpacingRange',
                                type=int,
                                required=True,
                                help="min of spacing range : Eg: -sr2 90 (in pixels)")

            parser.add_argument('-w',
                                '--imageWidth',
                                dest='imageWidth',
                                type=int,
                                required=True,
                                help='Image Width : Eg: -w 28 (in pixels)')

            args = parser.parse_args()

            if args.imageWidth < 0:
                message("{} is an invalid positive int value".format(args.imageWidth))
                parser.print_usage(sys.stdout)
                exit(1)

            if args.maxSpacingRange < args.minSpacingRange:
                message("maxSpacingRange :{} should be greater than minSpacingRange :{}".format(args.maxSpacingRange, args.minSpacingRange))
                parser.print_usage(sys.stdout)
                exit(1)

            logger.debug("Arguments : = {}".format(args))
            return dict(args._get_kwargs())

        except Exception as e:
            logger.error("Error while parsing CLI Arguments : {}".format(e))
            raise e


    def api_argument_parser(self):
        '''
        Api get parameter parsing function
        :return:
        '''

        help = jsonify(
            INFO='Usage for API',
            BASE_URL='http://127.0.0.1:5000/mdsg',
            QUERY_STRINGS='digits : Eg :[4 6 8], imageWidth : Eg :200, minSpacingRange : Eg : 7, maxSpacingRange : Eg : 9',
            EXAMPLE='http://127.0.0.1:5000/mdsg?d=4&d=5&d=8&sr1=3&sr2=9&w=100'
        )

        parser = reqparse.RequestParser()
        # parser.add_argument('rate', type=int, help='Rate to charge for this resource')
        # args = parser.parse_args()

        parser.add_argument('d',
                            dest='digits',
                            type=int,
                            choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                            required=True,
                            location='args',
                            action='append',
                            help='Missing : space separated digits to generate : Eg: d=3&d=8&d=1')

        parser.add_argument('sr1',
                            dest='minSpacingRange',
                            type=int,
                            required=True,
                            help="Missing : min of spacing range : Eg: sr1=30 (in pixels)")

        parser.add_argument('sr2',
                            dest='maxSpacingRange',
                            type=int,
                            required=True,
                            help="Missing : min of spacing range : Eg: sr2=90 (in pixels)")

        parser.add_argument('w',
                            dest='imageWidth',
                            type=int,
                            required=True,
                            help='Missing : Image Width : Eg: w=28 (in pixels)')

        args = parser.parse_args()

        if args.imageWidth < 0:
            message("{} is an invalid positive int value".format(args.imageWidth))
            return False, "{} is an invalid positive int value".format(args.imageWidth)

        if args.maxSpacingRange < args.minSpacingRange:
            message("maxSpacingRange :{} should be greater than minSpacingRange :{}".format(args.maxSpacingRange,
                                                                                      args.minSpacingRange))

            return False, "maxSpacingRange :{} should be greater than minSpacingRange :{}".format(args.maxSpacingRange,
                                                                                          args.minSpacingRange)
        logger.debug("Inputs : = {}".format(args))
        return True, args

#
# if __name__ == "__main__":
#     aa = CommandParser()
#     print(aa.cli_argument_parser())
