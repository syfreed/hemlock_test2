from hemlock import db
from hemlock.models.branch import Branch
from hemlock.models.page import Page

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_stack = db.relationship('Branch', backref='part', lazy='dynamic')
    curr_page = db.relationship('Page', uselist=False, backref='part')
        
    def get_page(self):
        return self.curr_page
        
    def advance_page(self):
        if not self.branch_stack.all():
            return False
        branch = self.branch_stack[-1]
        page = branch.dequeue()
        if page is None:
            self.terminate_branch(branch)
            return self.advance_page()
        self.curr_page = page
        return True
        
    def terminate_branch(self, branch):
        new_branch = branch.get_next()
        self.branch_stack.remove(branch)
        if new_branch is not None:
            new_branch.part = self