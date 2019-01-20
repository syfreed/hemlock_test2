from flask import render_template, redirect, url_for, session, request, Markup, make_response, request
from hemlock import app, db
from hemlock.models.participant import Participant
from hemlock.models.branch import Branch
from hemlock.models.page import Page
from hemlock.models.question import Question
import io
import csv

from survey import Start #

@app.route('/')
def index():
    db.create_all()
    
    part = Participant()
    session['part_id'] = part.id
    
    root = Branch(part=part, next=Start)
    part.advance_page()
    db.session.commit()
    
    return redirect(url_for('survey'))
    
@app.route('/survey', methods=['GET', 'POST'])
def survey():
    part = Participant.query.get(session['part_id'])
    page = part.get_page()
        
    if page.validate_on_submit():
        part.advance_page()
        db.session.commit()
        return redirect(url_for('survey'))
        
    if page.terminal:
        part.store_data()
        
    return render_template('page.html', page=Markup(page.render()))
    
@app.route('/download')
def download():
    # figure out how to download cleaned data
    data = Question.query.get(1).text
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow([data])
    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    output.headers['Context-type'] = 'text/csv'
    return output