##############################################################################
# Test a Hemlock survey
# by Dillon Bowen
# last modified 07/18/2019
##############################################################################

# TODO
# enter data into form fields

from hemlock.debug import main, AIParticipantBase
from unittest import TestCase

BATCH_SIZE = 3
NUM_BATCHES = 20

class AIParticipant(AIParticipantBase, TestCase):
    SURVEY_URL = 'https://test235711.herokuapp.com'
    P_REFRESH = 0.5
    P_BACK = 0.3

main(NUM_BATCHES, BATCH_SIZE)