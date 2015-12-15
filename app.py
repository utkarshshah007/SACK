from flask import Flask, jsonify, request, render_template, url_for, redirect
import json
import cx_Oracle
import os
import time
import urllib
from base64 import b64encode
import requests

app = Flask(__name__)
domain = "http://127.0.0.1:5000"
curruserid = 0
username = "d7e2536f-0268-41e3-b029-b4cb44161632"
password = "idCjPs9d3o4fTOrKSBPOM4fj9gxz7uHAsMxYY8Bv/YU"
to_rate = {}
idx_rate = {}
will_rate = set([])

@app.route('/')
def home():
    return 'Hello world.'

''' Login Methods '''
@app.route('/login')
def login():
    return render_template('test.html')

def login_user(email, password):
    query = """SELECT userid FROM USERS WHERE email = \'""" + email + """'"""
    results = cursor.execute(query).fetchone()
    print "hello"
    if results:
        global curruserid
        curruserid = results[0]
        return True
    else:
        return False

@app.route('/login', methods = ['POST'])
def accept_login():
    email = request.form['inputEmail']
    print email
    password = request.form['inputPassword']
    print password

    if login_user(email, password):
        return redirect(domain + "/suggestions", code=302)
    else:
        return redirect(url_for("register"), code=303)

@app.route('/loginfb', methods = ['POST'])
def fb_login():
    email = request.form['email']
    print email
    password = request.form['password']
    print password

    if login_user(email, password):
        return "/suggestions"
    else:
        redirect(url_for("registerfb"), code=307)


''''''

''' Signup Methods '''
@app.route('/register')
def register():
    return render_template('registerPage.html')

def new_registration(email, password):
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
        return error
        

@app.route('/register', methods = ['POST'])
def accept_registration():
    email = request.form['email']
    print email
    password = request.form['password']
    print password

    error = new_registration(email, password)
    if error:
        return render_template('registerPage.html', error = error)

    return redirect(domain + "/choose-genres", code=302)

@app.route('/registerfb', methods = ['POST'])
def accept_fb_registration():
    email = request.form['email']
    print email
    password = request.form['password']
    print password

    error = new_registration(email, password)
    if error:
        return "/register"
    
    return "/choose-genres"

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


def get_movies_to_rate(genre, num):
    all_movies = to_rate[genre]
    idx = idx_rate[genre]

    movies = []
    orig_idx = idx
    temp_idx = idx
    while idx < (orig_idx + num):
        movie = all_movies[temp_idx]
        if movie not in will_rate:
            will_rate.add(movie)
            movies.append(movie)
            idx += 1
        temp_idx += 1
    idx_rate[genre] = idx
    return movies


@app.route('/setup-rating/get-next-movie', methods = ['POST'])
def get_next_movie():
    genre = request.form['genre']
    mid, title = get_movies_to_rate(genre, 1)[0]
    movie = {}
    movie['mid'] = mid
    movie['movie_title'] = title
    return jsonify(movie)


''''''

'''setup-rating Methods'''
@app.route('/setup-rating')
def ask_for_setup_ratings():
    # get all genres to rate
    query = """SELECT gname
            FROM Prefer P
            INNER JOIN Users U ON U.userid = P.userid
            WHERE U.userid = """ + str(curruserid)

    results = cursor.execute(query).fetchall()
    genres = [genre[0] for genre in results]

    movies_to_rate = []
    for genre in genres:
        # get 50 movies/titles to rate in this genre
        query = """ SELECT M.mid, M.title
                    FROM Movies M
                    INNER JOIN PartOf P ON P.mid = M.mid
                    WHERE P.gname = \'""" + genre + """' 
                    ORDER BY M.countRatings DESC"""
        results = cursor.execute(query).fetchmany(numRows=50)
        
        # pull out 5 movies for the user to rate
        to_rate[genre] = results
        idx_rate[genre] = 0
        first_choice_movies = get_movies_to_rate(genre, 5)

        # format them so that we can use it in the template
        genre_movie = {}
        genre_movie['genre'] = genre
        movies = []
        for movie in first_choice_movies:
            movies.append({'id': movie[0], 'title': movie[1]})
        genre_movie['movies'] = movies
        movies_to_rate.append(genre_movie)
    return render_template('setupRatingScreen.html', genres = movies_to_rate)


''''''
'''Insert Rating in DB. Dont forget to commit later'''
def insert_rating(mid, rating):
    insert = """ INSERT INTO Rate (mid, rating, userid)
                     VALUES (""" + str(mid) + """, """ + str(rating) + """, 
                     """ + str(curruserid) + """)"""
    # TODO: Update average rating of movie
    cursor.execute(insert)


@app.route('/setup-rating', methods = ['POST'])
def accept_setup_ratings():
    for mid in request.form.keys():
        rating = request.form.getlist(mid)[0]
        insert_rating(mid, rating)
        
    connection.commit()
    return "/suggestions"


@app.route('/suggestions/rate-movie', methods = ['POST'])
def rate_movie():
    mid = request.form['mid']
    rating = request.form['rating']
    genre = request.form['genre']
    
    insert_rating(mid, rating)
    connection.commit()
    data = {'genre': genre}
    return jsonify(data)


@app.route('/suggestions/get-new-suggestion', methods = ['POST'])
def get_new_suggestion():
    mid = request.form['mid']
    genre = request.form['genre']
    insert = """ INSERT INTO Skip (userid, mid)
                     VALUES (""" + str(curruserid) + """, """ + str(mid) + """)"""
    cursor.execute(insert)
    connection.commit()
    data = {'genre': genre}
    return jsonify(data)

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
                INNER JOIN PartOf P ON M.mid = P.mid
                WHERE R.userid = """ + str(curruserid) + """ 
                AND R.rating >= 3 
                AND P.gname = '""" + genre + """'),
            sim_users AS
                (SELECT userid
                FROM rate R
                INNER JOIN fav_movies M ON M.mid = R.mid
                WHERE R.rating = 
                    (SELECT rating  
                     FROM Rate 
                     WHERE mid=M.mid 
                     AND userid = """ + str(curruserid) + """)
                GROUP BY userid
                HAVING count(rating) >= 3),
            movies_not_seen AS
                ((SELECT M.mid
                  FROM Movies M
                  INNER JOIN PartOf P ON P.mid = M.mid
                  WHERE P.gname = '""" + genre + """'
                  AND M.avgRating > 3.5)
                  MINUS
                ((SELECT M.mid
                 FROM Movies M
                 INNER JOIN Rate R ON R.mid = M.mid
                 INNER JOIN PartOf P ON P.mid = M.mid
                 WHERE P.gname = '""" + genre + """'
                 AND R.userid = """ + str(curruserid) + """)
                  UNION
                 (SELECT mid
                  FROM Skip
                  WHERE userid = """ + str(curruserid) + """)))
            SELECT M.mid
                FROM movies_not_seen M
                INNER JOIN Rate R ON R.mid = M.mid
                INNER JOIN sim_users U ON U.userid = R.userid
                GROUP BY M.mid
                ORDER BY avg(R.rating) DESC"""
    start_time = time.time()
    mid = cursor.execute(query).fetchone()[0]
    end_time = time.time()
    print ("time: " + str(end_time - start_time))
    query = """SELECT title, year, avgRating, countRatings, mid
               FROM Movies 
               WHERE mid = """ + str(mid)
    result = cursor.execute(query).fetchone()
    print result[0]
    picture = get_picture(result[0] + " movie poster")
    print picture
    return jsonify(title=result[0], year=result[1], avg_rating=result[2], num_ratings=result[3], mid=result[4], genre=genre, picture = picture)


def get_picture(name):
    print "get picture"
    name = name.encode('ascii', 'ignore')
    query = urllib.quote(name)
    headers = {
        "Authorization": 'Basic ' + b64encode("{0}:{1}".format(username, password))
    }
    print 'after create header'
    url = "https://api.datamarket.azure.com/Bing/Search/Image?%24format=json&ImageFilters=%27Aspect%3AWide%27&Query=%27" + query + "%27&$top=1" 
    print url
    r = requests.get(url, headers = headers)
    print 'after request'
    image_json = json.loads(r.text)
    return image_json["d"]["results"][0]["MediaUrl"]




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
    print "closing connection"
    cursor.close()
    connection.close()


def main():
    connectToDB()
    app.run()
    closeConnection()

if __name__ == '__main__':
    main()
