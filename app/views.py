from app import myapp, models
from flask import render_template, redirect, request, session, url_for, escape, flash
from .forms import QuestionForm
import requests, json, re, datetime

"""
View functions:
* Handle logic on the front-end
* Access the models file to use SQL functions
"""

# landing redirect
@myapp.route('/')
@myapp.route('/index')
def index():
	session.pop('page', None)
	session.pop('result', None)
	return render_template('index.html')

# display some random jokes
@myapp.route('/baseline', methods=['GET','POST'])
def baseline():

	jokes_df = models.get_random_jokes(20, random_state=42)
	jokes_idx = list(jokes_df.index)
	jokes_text = list(jokes_df['text'])

	# page: the current page/stage for the baseline, can be [1,2,3,4]
	page = 1 if 'page' not in session else int(session['page'])
	offset = (page - 1)*5

	form = QuestionForm()

	if form.validate_on_submit():
		# get user ratings from form data
		ratings = [field.data for field in form]
		# first field is CSRF field - remove that from the output
		ratings = ratings[1:]

		# result: a dictionary of joke ID: user rating so far
		# current result is stored as a variable in session
		result = dict() if 'result' not in session else json.loads(session['result'])
		for i in range(len(ratings)):
			result[str(jokes_idx[offset + i])] = ratings[i]
		session['result'] = json.dumps(result)

		# if reached last page, move onto next phase
		# otherwise increment page by 1
		if page == 4:
			return redirect('/update')
		else:
			session['page'] = str(page + 1)
			return redirect('/baseline')

	return render_template('baseline.html',
	jokes = jokes_text[offset:offset + 5], offset = offset, form = form)

@myapp.route('/update', methods=['GET','POST'])
def update():
	result = json.loads(session['result'])
	# TODO: Some ML magic here
	return render_template('update.html')

@myapp.route('/recommendation', methods=['GET','POST'])
def recommendation():
	jokes_df = models.get_random_jokes(5)
	jokes_idx = list(jokes_df.index)
	jokes_text = list(jokes_df['text'])

	form = QuestionForm()

	if form.validate_on_submit():
		# get user ratings from form data
		ratings = [field.data for field in form]
		# first field is CSRF field - remove that from the output
		ratings = ratings[1:]

		# result: a dictionary of joke ID: user rating so far
		result = dict()
		for i in range(len(ratings)):
			result[str(jokes_idx[i])] = ratings[i]

		# TODO: some dark ML magic should happen here!
		return redirect('/recommendation')

	return render_template('recommendation.html', jokes = jokes_text, form = form)

@myapp.route('/results', methods=['GET','POST'])
def results():
	result = json.loads(session['result'])
	return render_template('results.html', result = result)
