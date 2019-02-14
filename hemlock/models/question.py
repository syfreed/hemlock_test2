###############################################################################
# Question model
# by Dillon Bowen
# last modified 02/12/2019
###############################################################################

from hemlock import db
from hemlock.models.choice import Choice
from hemlock.models.validator import Validator
from hemlock.models.base import Base
from sqlalchemy import and_

# Renders errors from previous submit
def render_error(q):
    if q._error is None:
        return ''
    return '''
        <div style='color: #ff0000;'>
        {0}
        </div>
        '''.format(q._error)

# Renders question text in html format
def render_text(q):
    return '''
        {0}
        <br></br>
        '''.format(q._text)
        
# Renders the question body in html format
def render_body(q):
    if q._qtype == 'text':
        return ''
    if q._qtype == 'free':
        return render_free(q)
    if q._qtype == 'single choice':
        return render_single_choice(q)
    
# Renders free response question in html format
def render_free(q):
    default = q._default if q._default is not None else ''
    return '''
        <input name='{0}' type='text' value='{1}'>
        '''.format(q.id, default)
    
# Renders single choice question in html format
def render_single_choice(q):
    choices = q._choices.order_by('_order').all()
    [c._set_checked(c.id==q._default) for c in choices]
    choice_html = ['''
        <input name='{0}' type='radio' value='{1}' {2}>{3}
        <br></br>
        '''.format(q.id, c.id, c._checked, c._text) for c in choices]
    return ''.join(choice_html)

'''
Data:
_part_id: ID of participant to whom question belongs
_branch_id: ID of branch to which question belongs (embedded questions only)
_page_id: ID of page to which question belongs
_choices: list of choices (e.g. for single choice questions
_validators: list of validators
_order: order in which the question appears on the page
_text: question text
_qtype: question type
_var: variable to which the question contributes data
_all_rows: indicates that question data appears on all rows
_render_function: function called before redering the page
_render_args: arguments for the render function
_post_function: function called after responses are submitted and validated
_post_args: arguments for the post function
_randomize: indicator of choice randomization
_init_default: initial default option (before first post)
_default: participant's response from last post or initial default
_clear_on: list of situations in which question is cleared
_error: stores an error message if response was invalid
_response: participant's raw data response
_data: response data (cleaned version of response)
_vorder: order in which this question appears in its variable
_archive: copy of the question before it was rendered
'''
class Question(db.Model, Base):
    id = db.Column(db.Integer, primary_key=True)
    _part_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    _branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    _page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    _choices = db.relationship('Choice', backref='_question', lazy='dynamic')
    _validators = db.relationship('Validator', backref='_question', lazy='dynamic')
    _order = db.Column(db.Integer)
    _text = db.Column(db.Text)
    _qtype = db.Column(db.String(16))
    _var = db.Column(db.Text)
    _all_rows = db.Column(db.Boolean)
    _render_function = db.Column(db.PickleType)
    _render_args = db.Column(db.PickleType)
    _post_function = db.Column(db.PickleType)
    _post_args = db.Column(db.PickleType)
    _randomize = db.Column(db.Boolean)
    _init_default = db.Column(db.PickleType)
    _default = db.Column(db.PickleType)
    _clear_on = db.Column(db.PickleType)
    _error = db.Column(db.PickleType)
    _response = db.Column(db.Text)
    _data = db.Column(db.PickleType)
    _vorder = db.Column(db.Integer)
    
    # Adds question to database and commits on initialization
    def __init__(self, branch=None, page=None, order=None, text='', 
        qtype='text', var=None, all_rows=False,
        render=None, render_args=None,
        post=None, post_args=None,
        randomize=False, default=None, clear_on=[], data=None):
        
        self.var(var)
        self.branch(branch)
        self.page(page, order)
        self.text(text)
        self.qtype(qtype)
        self.all_rows(all_rows)
        self.render(render, render_args)
        self.post(post, post_args)
        self.randomize(randomize)
        self.default(default)
        self.clear_on(clear_on)
        self.data(data)
        
        db.session.add(self)
        db.session.commit()
        
    # Assign to branch
    def branch(self, branch):
        if branch is not None:
            self._assign_parent('_branch', branch, branch._embedded.all())
            if branch._part_id is not None:
                self._assign_participant(branch._part)
            
    # Remove from branch
    def remove_branch(self):
        self._part = None
        if self._branch is not None:
            self._remove_parent('_branch', self._branch._embedded.all())
    
    # Assign to page
    def page(self, page, order=None):
        if page is not None:
            self._assign_parent('_page', page, page._questions.all(), order)
            
    # Remove from page
    def remove_page(self):
        if self._page is not None:
            self._remove_parent('_page', self._page._questions.all())
            
    # Sets the question text
    def text(self, text):
        self._set_text(text)
        
    # Set question type
    def qtype(self, qtype):
        self._qtype = qtype
        
    # Set the variable in which question data will be stored
    def var(self, var):
        self._set_var(var)
        
    # Set the all_rows indicator
    # i.e. the data will appear in all of the participant's dataframe rows
    def all_rows(self, all_rows=True):
        self._set_all_rows(all_rows)
        
    # Set the render function and arguments
    def render(self, render=None, args=None):
        self._set_function('_render_function', render, '_render_args', args)
        
    # Set the post function and arguments
    def post(self, post=None, args=None):
        self._set_function('_post_function', post, '_post_args', args)
        
    # Turn randomization on/off (True/False)
    def randomize(self, randomize=True):
        self._set_randomize(randomize)
    
    # Set default answer
    # string for free response
    # choice id for multiple choice
    def default(self, default):
        self._init_default = default
        self._default = default
        
    # Set conditions for clearing the question
    # conditions are invalid, back, and forward
    def clear_on(self, clear_on):
        self._set_clear_on(clear_on)
        
    # Set question data
    def data(self, data):
        self._data = data
        
    # Get question data
    def get_data(self):
        return self._data
        
    # Get question response
    def get_response(self):
        return self._response
        
    # Get the list of selected choices
    def get_selected(self):
        return [c for c in self._choices if c._checked=='checked']
        
    # Get the list of nonselected choices
    def get_nonselected(self):
        [print(c._checked) for c in self._choices]
        return [c for c in self._choices if c._checked=='']
        
    # Render the question in html
    def _render_html(self):        
        if self._qtype == 'embedded':
            return ''
        return '''
        <p>
            {0}
            {1}
            {2}
        </p>
        '''.format(render_error(self), render_text(self), render_body(self))
        
    # Record the participant's response
    # collects response and updates default
    def _record_response(self, response):
        if self._qtype == 'free':
            self._default = response
        elif self._qtype == 'single choice':
            [c._set_checked(response==str(c.id)) for c in self._choices]
            checked = self.get_selected()
            if checked:
                self._default = checked[0].id
                response = checked[0]._value
        self._response = response
        self.data(response)
        
    # Validate the participant's response
    def _validate(self):
        for v in self._validators:
            self._error = v._get_error()
            if self._error is not None:
                # GIVE ERROR TO S1
                return False
        return True
        
    # Set the variable order
    def _set_vorder(self):
        if not self._var:
            return
        prev = Question.query.filter_by(_part_id=self._part_id, _var=self._var)
        self._vorder = len(prev.all())
        
    # Outputs the data (both question data and order data)
    def _output_data(self):
        # data, page order, and question order
        data = {
            self._var: self._data,
            self._var+'_porder': self._order,
            self._var+'_vorder': self._vorder}
            
        # choice order
        for c in self._choices:
            data['_'.join([self._var,c._label,'qorder'])] = c._order
            
        return data

    # Copies selected attributes of question q
    # def _copy(self, question_id):
        # q = Question.query.get(question_id)
    
        # self.branch(q._branch)
        # self.page(q._page)
        # self._set_order(q._order)
        # self.text(q._text)
        # self.qtype(q._qtype)
        # self.var(q._var)
        # self.all_rows(q._all_rows)
        # self.render(q._render_function, q._render_args)
        # self.post(q._post_function, q._post_args)
        # self.randomize(q._randomize)
        # self.default(q._init_default)
        # self._default = q._default
        # self.clear_on(q._clear_on)
        # self.rendered = False
        # self._error = q._error
        # self._response = q._response
        # self.data(q._data)
        # self._vorder = q._vorder
        
        # choices = [Choice(question=self)]*len(q._choices.all())
        # [new._copy(old.id) for (new,old) in zip(choices,q._choices)]

        # validators = [Validator(question=self)]*len(q._validators.all())
        # [new._copy(old.id) for (new,old) in zip(validators,q._validators)]
