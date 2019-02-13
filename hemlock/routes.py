###############################################################################
# URL routes for Hemlock survey
# by Dillon Bowen
# last modified 02/12/2019
###############################################################################

from hemlock import db, bp
from hemlock.models.participant import Participant
from hemlock.models.branch import Branch
from hemlock.models.page import Page
from hemlock.models.question import Question
from hemlock.models.variable import Variable
from flask import current_app, render_template, redirect, url_for, session, request, Markup, make_response, request
import io
import csv
import pandas as pd

# Create database tables upon survey launch
@bp.before_app_first_request
def before_first_app_request():
    db.create_all()

# Create participant and root branch before beginning survey
# (option) exlcude if duplicate ipv4
@bp.route('/')
def index():
    ipv4 = get_ipv4()
    if ipv4 in current_app.ipv4:
        return redirect(url_for('hemlock.exclude'))
    if current_app.block_duplicate_ips:
        current_app.ipv4.append(ipv4)
        
    part = Participant(ipv4)
    session['part_id'] = part.id
    root = Branch(next=current_app.start)
    root._assign_participant(part)
    part.advance_page()
    db.session.commit()
    
    return redirect(url_for('hemlock.survey'))
    
# Get user IPv4
def get_ipv4():
    ipv4 = request.environ.get('HTTP_X_FORWARDED_FOR', None)
    if ipv4 is None:
        return request.remote_addr
    return ipv4.split(',')[0]
        
# Exclude message
@bp.route('/exclude')
def exclude():
    page = Page(terminal=True)
    q = Question(page=page, text='''
        <p>Our records indicate that you have already participated in this or similar surveys.</p>
        <p>Thank you for your continuing interest in our research.</p>
        ''')
    return render_template('page.html', page=Markup(page._render_html()))
        
'''
Main survey route
alternate between GET and POST
    GET: render current page
    POST: collect and validate responses, advance to next page
store participant data on terminal page
'''
@bp.route('/survey', methods=['GET','POST'])
def survey():
    part = Participant.query.get(session['part_id'])
    page = part.get_page()
        
    if request.method == 'POST':
        if page._validate_on_submit():
            part.advance_page()
        db.session.commit()
        return redirect(url_for('hemlock.survey'))
        
    if page._terminal:
        page._render_html() # might change this when I record partial responses
        part.store_data()
        
    return render_template('page.html', page=Markup(page._render_html()))
    
'''
Download data
get data from all participants
write to csv and output
'''
@bp.route('/download')
def download():
    data = pd.concat([pd.DataFrame(p.data) for p in Participant.query.all()],
        sort=False) 
    resp = make_response(data.to_csv())
    resp.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    resp.headers['Content-Type'] = 'text/csv'
    return resp
    