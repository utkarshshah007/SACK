from flask import Flask, jsonify, request, render_template, url_for, redirect
import json
import cx_Oracle
import os

app = Flask(__name__)
domain = "http://127.0.0.1:5000"
curruserid = 0

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

    query = """SELECT userid FROM USERS WHERE email = \'""" + email + """'"""
    results = cursor.execute(query).fetchone()
    global curruserid
    curruserid = results[0]

    return redirect(domain + "/suggestions", code=302)

''''''

''' Signup Methods '''
@app.route('/register')
def register():
    return render_template('registerPage.html')

@app.route('/register', methods = ['POST'])
def accept_registration():
    email = request.form['email']
    print email
    password = request.form['password']
    print password

    query = """SELECT MAX(userid) FROM USERS"""
    result = cursor.execute(query).fetchone()
    global curruserid
    curruserid = result[0] + 1
    query = """INSERT INTO USERS (email, userid) 
            VALUES (\'""" + email + """', """ + str(curruserid) + """)"""
    try:
        cursor.execute(query)
        connection.commit()
        print "new user created"
    except cx_Oracle.IntegrityError:
        error = "Please use a different email. That email has already been registered."
        return render_template('registerPage.html', error = error)
    return redirect(domain + "/choose-genres", code=302)

''''''


'''Choose-Genres Methods'''
@app.route('/choose-genres')
def ask_for_genres():
    query = """SELECT * FROM GENRES"""
    results = cursor.execute(query).fetchall()
    genres = []
    for genre in results:
        genres.append({'name': genre[0] + "Checked", 'value': genre[0]})
    return render_template('setupGenreScreen.html', genres = genres)

@app.route('/choose-genres', methods = ['POST'])
def accept_genre_choices():
    genres = request.form.getlist('genre')
    for genre in genres:
        insert = """INSERT INTO Prefer (gname, userid)
                 VALUES (\'""" + genre +"""',""" + str(curruserid) +""")"""
        cursor.execute(insert)
    connection.commit()
    return redirect(domain + "/setup-rating", code=302)

''''''

'''setup-rating Methods'''
@app.route('/setup-rating')
def ask_for_setup_ratings():
    
    query = """SELECT gname
            FROM Prefer P
            INNER JOIN Users U ON U.userid = P.userid
            WHERE U.userid = """ + str(curruserid)
    results = cursor.execute(query).fetchall()
    genres = [genre[0] for genre in results]
    movies_to_rate = []
    for genre in genres:
        query = """ SELECT M.mid, M.title
                    FROM Movies M
                    INNER JOIN PartOf P ON P.mid = M.mid
                    WHERE P.gname = \'""" + genre + """'"""
        results = cursor.execute(query).fetchmany(numRows=5)
        genre_movie = {}
        genre_movie['genre'] = genre
        movies = []
        for movie in results:
            movies.append({'id': movie[0], 'title': movie[1]})
        genre_movie['movies'] = movies
        movies_to_rate.append(genre_movie)
    return render_template('setupRatingScreen.html', genres = movies_to_rate)

@app.route('/setup-rating', methods = ['POST'])
def accept_setup_ratings():
    for mid in request.form.keys():
        rating = request.form.getlist(mid)[0]

        insert = """ INSERT INTO Rate (mid, rating, userid)
                     VALUES (""" + str(mid) + """, """ + str(rating) + """, 
                     """ + str(curruserid) + """)"""
        cursor.execute(insert)
    connection.commit()
    return "/suggestions";


''''''

'''Suggestions Methods'''
@app.route('/suggestions')
def suggest_movies():
    query = """SELECT gname FROM Prefer P
            INNER JOIN Users U ON U.userid = P.userid
            WHERE U.userid = """ + str(curruserid)
    results = cursor.execute(query).fetchall()
    genres = [x[0] for x in results]

    return render_template('suggestMovies.html', genres = genres[1:], first_genre = genres[0])

@app.route('/suggestions', methods = ['POST'])
def suggest_movies_post():
    genre = request.form.getlist('genre')[0]
    query = """WITH fav_movies AS
            (SELECT M.mid
            FROM movies M
            INNER JOIN rate R ON M.mid = R.mid
            WHERE R.userid = """ + str(curruserid) + """ AND R.rating >= 3),
            sim_users AS
            (SELECT userid
            FROM rate R
            INNER JOIN fav_movies M ON M.mid = R.mid
            WHERE R.rating >= 3
            GROUP BY userid
            HAVING count(rating) >= 3),
            movies_not_seen AS
            ((SELECT M.mid
              FROM Movies M)
              MINUS
            (SELECT M.mid
             FROM Movies M
             INNER JOIN Rate R ON R.mid = M.mid
             WHERE R.userid = """ + str(curruserid) + """)),
            suggested_movies AS
            (SELECT M.mid, avg(R.rating) AS avgRating
            FROM movies_not_seen M
            INNER JOIN Rate R ON R.mid = M.mid
            INNER JOIN sim_users U ON U.userid = R.userid
            INNER JOIN PartOf P ON P.mid = M.mid
            WHERE P.gname = '""" + genre + """'
            GROUP BY M.mid)
            SELECT mid
            FROM suggested_movies 
            WHERE avgRating >= ALL (SELECT avgRating FROM suggested_movies)"""
    mid = cursor.execute(query).fetchone()[0]
    query = """SELECT title, year, avgRating
               FROM Movies 
               WHERE mid = """ + str(mid)
    result = cursor.execute(query).fetchone()
    print result
    return jsonify(title=result[0], year=result[1], avg_rating=result[2])




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

def connectToDB():
    ip = 'cis550.cfserwqjknt5.us-east-1.rds.amazonaws.com'
    port = 1521
    SID = 'ORCL'

    dsn_tns = cx_Oracle.makedsn(ip, port, SID)
    global connection 
    connection = cx_Oracle.connect('groupsack', 'sackgroup', dsn_tns)

    print "connection successful"
    global cursor 
    cursor = connection.cursor()
    

def closeConnection():
    cursor.close()
    connection.close()
    print "connection closed"

def main():
    #app.debug = True
    #port = int(os.environ.get("PORT", 5000))
    connectToDB()
    app.run()
    closeConnection()

if __name__ == '__main__':
    main()
