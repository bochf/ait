"""
Generate test cases from a given state machine
"""

import argparse
import textwrap
import logging


def _init_log(filename, level=logging.DEBUG):
    logging.basicConfig(filename=filename, level=level)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="input file name")
    parser.add_argument(
        "-s",
        "--strategy",
        choices=["node", "path", "euler"],
        default="path",
        help=textwrap.dedent(
            """the case generating strategy:\
                             node: generate one case from the given start node to the end node
                             path: generate all the cases for all the state transitions
                             euler: generate all the cases with least redundant transitions
                             """
        ),
    )
    parser.add_argument("-b", "--begin", default=0, help="the begin node")
    parser.add_argument("-e", "--end", default=0, help="the end node")
    parser.add_argument("-p", "--print", action="store_true", help="print the graph")
    parser.add_argument("-l", "--log", default="casegen.log", help="log file name")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug mode")

    return parser.parse_args()


if __name__ == "__main__":
    print("generate test case")

    options = _parse_args()
    log_level = logging.DEBUG if options.verbose else logging.INFO
    _init_log(options.log, log_level)

    logging.debug("Program starts. options=%s", options)
