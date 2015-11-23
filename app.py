from flask import Flask, jsonify, request, render_template, url_for, redirect
import json
import os

app = Flask(__name__)
domain = "http://127.0.0.1:5000"

@app.route('/')
def home():
    return 'Hello world.'

''' Login Methods '''
@app.route('/login')
def login():
    return render_template('test.html')

@app.route('/login', methods = ['POST'])
def accept_login():
    email = request.form['inputEmail']
    print email
    password = request.form['inputPassword']
    print password

    return redirect(domain + "/choose-genres", code=302)

''''''

'''Choose-Genres Methods'''
@app.route('/choose-genres')
def ask_for_genres():
    return render_template('setupGenreScreen.html')

@app.route('/choose-genres', methods = ['POST'])
def accept_genre_choices():
    choices = []
    if 'actionChecked' in request.form:
        choices.append("action")
    if 'adventureChecked' in request.form:
        choices.append("adventure")
    if 'mysteryChecked' in request.form:
        choices.append("mystery")
    print choices

    return redirect(domain + "/setup-rating", code=302)

''''''

'''Choose-Genres Methods'''
@app.route('/setup-rating')
def ask_for_setup_ratings():
    return render_template('setupRatingScreen.html')

@app.route('/setup-rating', methods = ['POST'])
def accept_setup_ratings():
    pass

''''''

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

def main():
    #app.debug = True
    #port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)

if __name__ == '__main__':
    main()