###############################################################################
# Main file for Hemlock surveys
# by Dillon Bowen
# last modified 01/21/2019
###############################################################################

from survey import Start
from config import Config
from hemlock import create_app, db
from hemlock.query import query
from hemlock.models.participant import Participant
from hemlock.models.branch import Branch
from hemlock.models.page import Page
from hemlock.models.question import Question
from hemlock.models.variable import Variable

app = create_app(Config, Start)

@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'query': query, 'Participant': Participant, 'Branch': Branch, 'Page': Page, 'Question': Question, 'Variable': Variable}