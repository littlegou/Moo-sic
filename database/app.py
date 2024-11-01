from flask import Flask, render_template, request, redirect, url_for, flash, session
from DB import get_db_connection
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

connection = get_db_connection()

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
app = Flask(__name__, template_folder=template_dir,static_folder=static_dir)
app.secret_key = 'your_secret_key'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/m')
def m():
    return render_template('m.html')

@app.route('/settings', methods =['GET', 'POST'])
def settings():
    return render_template('settings.html')

@app.route('/calendar', methods =['GET', 'POST'])
def calendar():
    return render_template('calendar.html')

@app.route('/recommend', methods =['GET', 'POST'])
def recommend():
    return render_template('recommend.html')

@app.route('/karaoke', methods =['GET', 'POST'])
def karaoke():
    return render_template('karaoke.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = connection.cursor(buffered=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user[2], password):
            session['loggedin'] = True
            session['username'] = user[0]
            mesage = 'Logged in successfully !'
            return redirect(url_for('m'))
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
        cursor = connection.cursor(buffered=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        cursor = connection.cursor(buffered=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        accusn = cursor.fetchone()

        if account:
            mesage = 'Email already exists !'
        elif accusn:
            mesage = 'Username already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not username or not password or not email:
            mesage = 'Please fill out the form !'
        elif password == username:
            mesage = 'Please fill out the form !'
        elif len(password) < 8:
            mesage = 'Please fill you password more than 8 letters !'
        else:
            hashed_password = generate_password_hash(password)
            cursor = connection.cursor(buffered=True)
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
            connection.commit()
            mesage = 'You have successfully registered !'
            return render_template('login.html')
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('signup.html', mesage = mesage)

@app.route('/select_mood', methods=['GET', 'POST'])
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
    username = session.get('username')
    favorite_songs = []
    mood = request.args.get('mood')
    reason = request.args.get('reason')
    if (mood != session.get('mood') and mood) or (reason != session.get('reason') and reason):
        session['mood'] = mood
        session['reason'] = reason
        session['current_song'] = []
        print(session)
    if 'refresh' in request.args:
        print(session)
        query = "SELECT mood, why FROM song WHERE song_name = %s"
        songname = session.get('current_song')[0][0]
        with connection.cursor() as cursor:
            cursor.execute(query, (songname,))
            md = cursor.fetchone()
        print(session)
        mood = md[0]
        reason = md[1]
        print(mood,reason)
        if mood and reason:
            query = "SELECT song_name, artist, embed FROM song WHERE mood = %s AND why = %s ORDER BY RAND() LIMIT 1"
            with connection.cursor() as cursor:
                cursor.execute(query, (mood, reason))
                songs = cursor.fetchall()
                session['current_song'] = songs
    elif session['current_song'] == []:
        print("sur")
        mood = request.args.get('mood')
        reason = request.args.get('reason')
        if mood and reason:
            session['mood'] = mood
            session['reason'] = reason
            
            query = "SELECT song_name, artist, embed FROM song WHERE mood = %s AND why = %s ORDER BY RAND() LIMIT 1"
            with connection.cursor() as cursor:
                cursor.execute(query, (mood, reason))
                songs = cursor.fetchall()

            if songs:
                session['current_song'] = songs
                print(songs)

    if username:
        with connection.cursor() as cursor:
            check_fav_query = "SELECT Song, Artists, yt FROM favorites WHERE username = %s"
            cursor.execute(check_fav_query, (username,))
            favorite_songs = cursor.fetchall()

    if request.method == 'POST':
        if 'add_fav' in request.form:
            song_name = request.form.get('song_name')
            artist = request.form.get('artist')
            query = "SELECT yt FROM song WHERE song_name = %s"
            with connection.cursor() as cursor:
                cursor.execute(query, (song_name,))
                result = cursor.fetchone()

                if result:
                    youtube_link = result[0]

                    if username and song_name and artist:
                        check_fav_query = "SELECT * FROM favorites WHERE username = %s AND Song = %s"
                        cursor.execute(check_fav_query, (username, song_name))
                        existing_favorite = cursor.fetchone()

                        if not existing_favorite:
                            insert_query = "INSERT INTO favorites (id, username, Song, Artists, yt) VALUES (NULL, %s, %s, %s, %s)"
                            cursor.execute(insert_query, (username, song_name, artist, youtube_link))
                            connection.commit()
                            with connection.cursor() as cursor:
                                check_fav_query = "SELECT Song, Artists, yt FROM favorites WHERE username = %s"
                                cursor.execute(check_fav_query, (username,))
                                favorite_songs = cursor.fetchall()
                    return render_template('randomsong.html', songs=session['current_song'][0], favorite_songs=favorite_songs)
        elif 'add_song' in request.form:
            new_song_name = request.form.get('new_song_name')
            new_artist = request.form.get('new_artist')
            youtube_link = request.form.get('youtube_link')
            new_mood = request.form.get('mood')
            new_why = request.form.get('reason')
            if "&list=" in youtube_link:
                a = youtube_link[:youtube_link.find("&list=")]
            else:
                a = youtube_link
            if "https://www.youtube.com/watch?v=" in a:
                a = a.replace("https://www.youtube.com/watch?v=","")
            elif "&list=" in a:
                a = a[:a.find("&list=")]
            elif "https://youtu.be/" in a:
                a = a.replace("https://youtu.be/","")
            else:
                a = a.replace("https://www.youtube.com/","")
            new_embed = "<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/"+ a + "\" title=\"YouTube video player\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share\" referrerpolicy=\"strict-origin-when-cross-origin\" allowfullscreen></iframe>"
            check_query = "SELECT * FROM song WHERE song_name = %s"
            with connection.cursor() as cursor:
                cursor.execute(check_query, (new_song_name,))
                existing_song = cursor.fetchone()

            if existing_song:
                flash('เพลงนี้มีอยู่แล้ว!')
            else:
                if youtube_link:
                    insert_query = "INSERT INTO song (song_id, song_name, Artist, Mood, Why, yt, Embed) VALUES (NULL, %s, %s, %s, %s, %s, %s)"
                    with connection.cursor() as cursor:
                        cursor.execute(insert_query, (new_song_name, new_artist, new_mood, new_why, youtube_link, new_embed))
                        connection.commit()
                flash('เพิ่มเพลงใหม่เรียบร้อย!')
            return render_template('randomsong.html', songs=session['current_song'][0], favorite_songs=favorite_songs)

    mood = request.args.get('mood')
    reason = request.args.get('reason')
    session['mood'] = mood
    session['reason'] = reason
    print(session)
    print(mood,reason)
    current_song = session.get('current_song')
    print(current_song)
    return render_template('randomsong.html', songs=current_song[0], favorite_songs=favorite_songs)

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        
        cursor = connection.cursor(buffered=True)
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
