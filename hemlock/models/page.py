###############################################################################
# Page model
# by Dillon Bowen
# last modified 01/21/2019
###############################################################################

from flask import request
from hemlock import db
from hemlock.models.question import Question
from random import choice
from string import ascii_letters, digits

# Create a hidden tag for form (for security purposes)
def hidden_tag():
    tag = ''.join([choice(ascii_letters + digits) for i in range(90)])
    return "<input name='crsf_token' type='hidden' value='" + tag + "'>"

# Data:
# ID of participant to whom the page belongs
# ID of branch to which the page belongs
# List of questions
# Indicator of whether form submission is valid
# Indicator of whether this page is terminal
# Order in which the page appears in its branch
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('participant.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    questions = db.relationship('Question', backref='page', lazy='dynamic')
    valid = db.Column(db.Boolean, default=False)
    terminal = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer)
    
    # Add to database and commit upon initialization
    def __init__(self, branch=None, order=None, terminal=False):
        self.assign_branch(branch, order)
        self.set_terminal(terminal)
        db.session.add(self)
        db.session.commit()
    
    # Assign to branch
    # removes from current branch (if any)
    # adds itself to the new branch queue (default at end of queue)
    def assign_branch(self, branch, order=None):
        if self.branch:
            self.branch.remove_page(self)
        self.branch = branch
        self.set_order(order)
        
    # Set the order in which the page appears in its branch
    # appears at the end of the branch by default
    def set_order(self, order=None):
        if order is None and self.branch:
            order = len(self.branch.page_queue.all()) - 1
        self.order = order
        
    # Indicates whether the page is terminal
    def set_terminal(self, terminal=True):
        self.terminal = terminal
        
    # Remove a question from page
    # reset order remaining pages
    def remove_question(self, question):
        self.questions.remove(question)
        questions = self.questions.order_by('order')
        for i in range(len(self.questions.all())):
            questions[i].set_order(i)
    
    # Render the html code for the form specified on this page
    # adds a hidden tag
    # renders html for each question
    # adds a submit button for non-terminal pages
    def render(self):
        rendered_html = hidden_tag()
        for question in self.questions.order_by('order'):
            rendered_html += question.render(self.part)
        if not self.terminal:
            rendered_html += "<p align=right><input type='submit' name='submit' value='>>'></p>"
        return rendered_html
        
    # Checks if questions have valid answers upon page submission
    def validate_on_submit(self):
        if request.method == 'POST':    
            for question in self.questions:
                question.set_data(request.form.get(str(question.id)))
                # ADD QUESTION VALIDATION HERE
        return request.method == 'POST'