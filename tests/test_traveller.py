import logging
from ait.traveller import Hierholzer


def test_find_itinerary():
    tickets = [[0, 1], [1, 2], [2, 3], [2, 4], [4, 5], [5, 6], [6, 2], [3, 1]]
    travel = Hierholzer(tickets)
    output = travel.find_itinerary()

    logging.info("input: %s", tickets)
    logging.info("output: %s", output)
