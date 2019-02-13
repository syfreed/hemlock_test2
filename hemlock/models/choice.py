###############################################################################
# Choice model
# by Dillon Bowen
# last modified 02/12/2019
###############################################################################

from hemlock import db
from hemlock.models.base import Base

'''
Data:
_question_id: ID of the question to which the choice belongs
_order: order in which the choice appears in the question
_text: choice text
_value: encoded value of the choice
_value_followstext: indicates whether the choice value follows the text
_label: choice label, used to record order data
_label_followtext: indicates whether the choice label follows the text
_checked: indicator that this choice was checked
'''
class Choice(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    _question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    _order = db.Column(db.Integer)
    _text = db.Column(db.Text)
    _value = db.Column(db.PickleType)
    _value_followstext = db.Column(db.Boolean, default=True)
    _label = db.Column(db.String(16))
    _label_followtext = db.Column(db.Boolean, default=True)
    _checked = db.Column(db.String(8))
    
    # Add choice to database and commit on initialization
    def __init__(self, question=None, order=None, text='', 
        value=None, label=None):
        
        self.assign_question(question, order)
        self.text(text)
        self.value(value)
        self.label(label)
        
        db.session.add(self)
        db.session.commit()
        
    # Assign to question
    def assign_question(self, question, order=None):
        if question is not None:
            self._assign_parent('_question', question, question._choices.all(), order)
        
    # Remove from question
    def remove_question(self):
        if self._question is not None:
            self._remove_parent('_question', self._question._choices.all())
        
    # Set the choice text
    def text(self, text):
        self._set_text(text)
        if self._value_followstext:
            self._value = text
        if self._label_followtext:
            self._label = text
        
    # Get the choice text
    def get_text(self):
        return self._text
        
    # Set the encoded value of the choice
    def value(self, value=None):
        if value is None:
            self._value = self._text
            self._value_followstext = True
        else:
            self._value = value
            self._value_followstext = False
            
    # Set the choice label
    def label(self, label=None):
        if label is None:
            self._label = self._text
            self._label_followtext = True
        else:
            self._label = label
            self._label_followtext = False
            
    # Set the choice as checked
    def _set_checked(self, checked=True):
        self._checked = 'checked' if checked else ''