###############################################################################
# Question model
# by Dillon Bowen
# last modified 01/21/2019
###############################################################################

from hemlock import db
from hemlock.models.choice import Choice
from hemlock.models.validator import Validator
from random import shuffle

# Renders errors from previous submit
def render_errors(q):
    error_html = ['''
        <div style='color: #ff0000;'>
        {0}
        </div>
        '''.format(error)
        for error in q.errors]
    return ''.join(error_html)

# Renders question text in html format
def render_text(q):
    return '''
        {0}
        <br></br>
        '''.format(q.text)
        
# Renders the question body in html format
def render_body(q):
    if q.qtype == 'text':
        return ''
    if q.qtype == 'free':
        return render_free(q)
    if q.qtype == 'single choice':
        return render_single_choice(q)
    
# Renders free response question in html format
def render_free(q):
    return '''
        <input name='{0}' type='text' value='{1}'>
        '''.format(q.id, q.default)
    
# Renders single choice question in html format
def render_single_choice(q):
    choices = q.choices.order_by('order').all()
    if q.randomize:
        shuffle(choices)
    choice_html = ['''
        <input name='{0}' type='radio' value='{1}'>{2}
        <br></br>
        '''.format(q.id, c.value, c.text) for c in choices]
    return ''.join(choice_html)

# Data:
# ID of participant to whom the question belongs
# ID of the branch to which the question belongs (for embedded data only)
# ID of the page to which the question belongs
# Question type (qtype)
# Variable in which the question data will be stored
# Text
# Default answer
# Data
# Order in which question appears on page
# All_rows indicator
#   i.e. the question data will appear in all of its participant's rows
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    choices = db.relationship('Choice', backref='question', lazy='dynamic')
    validators = db.relationship('Validator', backref='question', lazy='dynamic')
    qtype = db.Column(db.String(16))
    var = db.Column(db.Text)
    text = db.Column(db.Text)
    randomize = db.Column(db.Boolean)
    default = db.Column(db.Text)
    data = db.Column(db.Text)
    order = db.Column(db.Integer)
    errors = db.Column(db.PickleType, default=[])
    all_rows = db.Column(db.Boolean)
    
    # Adds question to database and commits on initialization
    def __init__(self, branch=None, page=None, order=None, var=None, 
        qtype='text', text='', randomize=False, default='', data=None, 
        all_rows=False):
        
        self.set_qtype(qtype)
        self.branch = branch
        self.assign_page(page, order)
        self.set_var(var)
        self.set_text(text)
        self.set_randomize(randomize)
        self.set_default(default)
        self.set_data(data)
        self.set_all_rows(all_rows)
        db.session.add(self)
        db.session.commit()
    
    # Assign to page
    # removes question from old page (if any)
    # assigns question to new page
    # adds itself to the new page question list (default at end)
    def assign_page(self, page, order=None):
        if self.page:
            self.page.remove_question(self)
        self.page = page
        self.set_order(order)
        
    # Set the order in which the question appears in its page
    # appears at the end of the page by default
    def set_order(self, order=None):
        if order is None and self.page:
            order = len(self.page.questions.all()) - 1
        self.order = order
        
    # Set the variable in which question data will be stored
    def set_var(self, var):
        self.var = var
        
    # Set question type (default text only)
    def set_qtype(self, qtype):
        self.qtype = qtype
    
    # Set text
    def set_text(self, text):
        self.text = text
        
    # Set randomization
    def set_randomize(self, randomize=True):
        self.randomize = randomize
        
    # Add choice
    def add_choice(self, text='', value=None, order=None):
        choice = Choice(question=self, text=text, value=value, order=order)
        
    # Add validation
    def add_validation(self, condition, message=None):
        validation = Validator(question=self, condition=condition, message=message)
    
    # Set default answer
    def set_default(self, default):
        self.default = default
        
    # Set the data
    def set_data(self, data):
        self.data = data
        
    # Set the all_rows indicator
    # i.e. the question data will appear in all of its participant's rows
    def set_all_rows(self, all_rows):
        self.all_rows = all_rows
        
    # Render the question in html
    # assign to participant upon rendering
    def render(self, part):
        self.part = part
        db.session.commit()
        
        if self.qtype == 'embedded':
            return ''
            
        return '''
        <p>
            {0}
            {1}
            {2}
        </p>
        '''.format(render_errors(self), render_text(self), render_body(self))
        
    # Validate an answer
    def validate(self):
        self.errors = [v.message for v in self.validators if not v.validate()]
        return not self.errors