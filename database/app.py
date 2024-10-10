from flask import Flask, render_template, request, redirect, url_for, flash, session
from DB import get_db_connection
import os
import re
connection = get_db_connection()

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
app = Flask(__name__, template_folder=template_dir,static_folder=static_dir)
app.secret_key = 'your_secret_key'

# @app.route('/')
# def main():
#     return render_template('index.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['loggedin'] = True
            session['username'] = user['username']
            session['password'] = user['password']
            mesage = 'Logged in successfully !'
            return render_template('selectmood.html', mesage = mesage)
        else:
            mesage = 'Please enter correct username / password !'
    return render_template('login.html', mesage = mesage)

@app.route('/sign_up', methods =['GET', 'POST'])
def sign_up():
    mesage = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not username or not password or not email:
            mesage = 'Please fill out the form !'
        elif password == username:
            mesage = 'Please fill out the form !'
        elif len(password) < 8:
            mesage = 'Please fill you password more than 8 letters !'
        else:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            connection.commit()
            mesage = 'You have successfully registered !'
            return render_template('login.html')
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('signup.html', mesage = mesage)

@app.route('/select_mood')
def select_mood():
    return render_template('selectmood.html')

@app.route('/sad', methods=['GET', 'POST'])
def sad():
    return render_template('sad.html')

@app.route('/happy', methods=['GET', 'POST'])
def happy():
    return render_template('happy.html')

@app.route('/randomsong', methods=['GET', 'POST'])
def randomsong():
    if request.method == 'POST':
        song_name = request.form.get('song_name')
        artist = request.form.get('artist')
        username = session.get('username')
        print(song_name,username,artist)
        query = "SELECT yt FROM song WHERE song_name = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (song_name,))
            result = cursor.fetchone()

            if result:
                youtube_link = result[0]

                if username and song_name and artist:
                    check_fav_query = "SELECT * FROM favorites WHERE username = %s AND Song = %s"
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(check_fav_query, (username, song_name))
                    existing_favorite = cursor.fetchone()

                    if not existing_favorite:
                        insert_query = "INSERT INTO favorites (id, username, Song, Artists, yt) VALUES (NULL, %s, %s, %s, %s)"
                        with connection.cursor() as cursor:
                            cursor.execute(insert_query, (username, song_name, artist, youtube_link))
                            connection.commit()
        return redirect(url_for('profile'))

    mood = request.args.get('mood')
    why = request.args.get('why')

    query = "SELECT song_name, artist, embed FROM song WHERE mood = %s AND why = %s ORDER BY RAND() LIMIT 1"
    with connection.cursor() as cursor:
        cursor.execute(query, (mood, why))
        songs = cursor.fetchall()
    print(songs)
    return render_template('randomsong.html', songs=songs)

@app.route('/')
def findbug():
    with connection.cursor() as cursor:
        cursor.execute('SELECT Embed FROM song')
        songs = cursor.fetchall()
    return render_template('findbug.html', songs=songs)

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT Song, Artists, yt FROM favorites WHERE username = %s', (username,))
        songs = cursor.fetchall()
        cursor.close()
        print(songs)
        return render_template('profile.html', username=username, songs=songs)


@app.route('/excited', methods=['GET', 'POST'])
def excited():
    return render_template('excited.html')

@app.route('/inspiration', methods=['GET', 'POST'])
def inspiration():
    return render_template('inspiration.html')

@app.route('/anger', methods=['GET', 'POST'])
def anger():
    return render_template('anger.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('usename', None)
    session.pop('password', None)
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)
