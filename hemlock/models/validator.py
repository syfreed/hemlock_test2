###############################################################################
# Validator model
# by Dillon Bowen
# last modified 03/17/2019
###############################################################################

from hemlock.factory import db
from hemlock.models.private.base import Base

'''
Data:
_question_id: ID of the question to which the validator belongs
_order: order in which validation appears in question
_condition_function: function which validates participant's response
_condition_args: arguments for the condition function
'''
class Validator(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    
    _question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    _index = db.Column(db.Integer)
    
    _condition_function = db.Column(db.PickleType)
    _condition_args = db.Column(db.PickleType)
    
    # Add to database and commit on initialize
    def __init__(self, question=None, condition=None, args=None, index=None):
        db.session.add(self)
        db.session.commit()
        
        self.question(question, index)
        self.condition(condition, args)
        
    # Assign to question
    def assign_question(self, question, index=None):
        self._assign_parent(question, '_question', index)
        
    # Remove from question
    def remove_question(self):
        self._remove_parent('_question')
        
    # Set the condition function and arguments
    def condition(self, condition=None, args=None):
        self._set_function('_condition_function', condition, '_condition_args', args)
        
    # Return error message if response is invalid
    # return None if response was valid
    def _get_error(self):
        return self._call_function(
            self._question, self._condition_function, self._condition_args)