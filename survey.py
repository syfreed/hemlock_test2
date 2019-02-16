###############################################################################
# Example Hemlock survey
# by Dillon Bowen
# last modified 02/15/2019
###############################################################################

'''
syntax: x = even_randomize(tag, nested list or tuples, choose_num, combination)
MIGHT HAVE TO DO DEEP COPIES TO CHANGE ARGS
'''

from hemlock import create_app, db, query, restore_branch, even_randomize, random_assignment, Participant, Branch, Page, Question, Choice, Validator, Variable, Randomizer
from config import Config
import pandas as pd
import numpy as np
from random import choice

#https://getbootstrap.com/docs/4.0/components/forms/

def Start():
    b = Branch()
    
    disclosed = [0,1]
    smart_anchor = [0,1]
    disclosed, smart_anchor = random_assignment(b,'condition',
        ['disclosed', 'smart_anchor'], [disclosed, smart_anchor])
    
    p = Page(b, terminal=True)
    q = Question(p, render=disp, render_args=[disclosed, smart_anchor])
    
    return b
    
def disp(q, assignments):
    disclosed, smart_anchor = assignments
    if disclosed:
        knowledge = 'disclosed'
    else:
        knowledge = 'surprise'
    if smart_anchor:
        anchor = 'smart anchor'
    else:
        anchor = 'no anchor'
    q.text('You are in the {0} {1} condition'.format(knowledge, anchor))
        
app = create_app(Config, 
    start=Start, 
    block_duplicate_ips=False,
    block_from_csv='block.csv')

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'query':query, 'restore_branch':restore_branch, 'even_randomize':even_randomize, 'random_assignment':random_assignment,'Participant':Participant, 'Branch':Branch, 'Page':Page, 'Question':Question, 'Choice':Choice, 'Validator':Validator, 'Variable':Variable, 'pd':pd, 'np':np, 'Randomizer':Randomizer}