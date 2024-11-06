from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from DB import get_db_connection
import os
import re
from karaoke import songs_karaoke
from werkzeug.security import generate_password_hash, check_password_hash

connection = get_db_connection()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
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
    usn = session.get('username')
    print(session)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if 'username' in request.form:
            cursor = connection.cursor(buffered=True)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            accusn = cursor.fetchone()
            if accusn and username:
                flash('Username already exists!')
            elif username:
                update_query = ' UPDATE users SET username = %s WHERE username = %s'
                cursor = connection.cursor(buffered=True)
                cursor.execute(update_query, (username, usn))
                connection.commit()
                cursor.close()
                session['username'] = username
                flash("Username updated successfully.")
        if 'password' in request.form:
            if 0 < len(password) < 8 :
                flash('Please fill your password with more than 8 letters!')
            elif len(password) >= 8:
                hashed_password = generate_password_hash(password)
                print(hashed_password)
                cursor = connection.cursor(buffered=True)
                update_query = ' UPDATE users SET password = %s WHERE username = %s'
                cursor.execute(update_query, (hashed_password, usn))
                connection.commit()
                cursor.close()
                flash("Password updated successfully.")
        if 'email' in request.form :
            cursor = connection.cursor(buffered=True)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            em = cursor.fetchone()
            if em and email:
                flash('Email already exists!')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email) and email:
                flash('Invalid email address!')
            elif email:
                update_query = ' UPDATE users SET email = %s WHERE username = %s'
                cursor = connection.cursor(buffered=True)
                cursor.execute(update_query, (email, usn))
                connection.commit()
                cursor.close()
                flash("Email updated successfully.")
    return render_template('settings.html')

@app.route('/recommend', methods =['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        name = request.form['name']
        song_name = request.form['song_name']
        artist = request.form['artist']
        yt = request.form['yt']
        reason = request.form['reason']

        if not (name and song_name and artist and yt and reason):
            flash('กรุณากรอกข้อมูลให้ครบถ้วน', 'danger')
            return redirect(url_for('recommend'))

        cursor = connection.cursor(buffered=True)
        cursor.execute("INSERT INTO postits(name, song_name, artist, yt, reason) VALUES(%s, %s, %s, %s, %s)",
                    (name, song_name, artist, yt, reason))
        connection.commit()
        cursor.close()

        flash('เพิ่มบันทึกเพลงสำเร็จ!', 'success')
        return redirect(url_for('recommend'))

    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT * FROM postits")
    postits = cursor.fetchall()


    return render_template('recommend.html', postits=postits)

@app.route('/selectsongforkaraoke')
def selectsongforkaraoke():
    return render_template('selectsongforkaraoke.html', songs_karaoke=songs_karaoke)

@app.route('/karaoke')
def karaoke():
    song_id = request.args.get('song_id')
    selected_song = next((song for song in songs_karaoke if song['song_id'] == song_id))
    if selected_song:
        return render_template('karaoke.html',song_name=selected_song['title'],artist = selected_song['artist'],youtube_video_id=selected_song['youtube_id'],lyrics_with_timings=selected_song['lyrics_with_timings'])

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

@app.route('/selectmoodforcalendar', methods=['GET', 'POST'])
def selectmoodforcalendar():
    date = request.args.get('date')
    date = date.split("-")
    date[1] = str(int(date[1]) + 1)
    date = "-".join(date)
    session['date'] = date
    return render_template('selectmoodforcalendar.html')

@app.route('/randomsongforcalendar', methods=['GET', 'POST'])
def randomsongforcalendar():
    username = session.get('username')
    favorite_songs = []
    mood = request.args.get('mood')
    reason = request.args.get('reason')
    session['mood'] = mood
    session['reason'] = reason
    
    query = "SELECT song_name, artist, embed ,yt FROM song WHERE mood = %s AND why = %s ORDER BY RAND() LIMIT 1"
    with connection.cursor() as cursor:
        cursor.execute(query, (mood, reason))
        songs = cursor.fetchall()

    if songs:
        print(mood,reason)
        session['fav'] = songs
        session['mood'] = mood
        session['reason'] = reason

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
            return render_template('randomsongforcalendar.html', songs=session['fav'][0], favorite_songs=favorite_songs)
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
            return render_template('randomsongforcalendar.html', songs=session['fav'][0], favorite_songs=favorite_songs)
        elif 'submit_description' in request.form:
            date = session.get('date')
            username = session.get('username')
            song = session.get('fav')
            description = request.form.get('description')
            cursor = connection.cursor(buffered=True)
            cursor.execute('SELECT mood FROM song WHERE song_name = %s', (session['fav'][0][0],))
            mood = cursor.fetchall()
            m = {"Angry":"IMGanger.PNG","Sad":"IMGsad.PNG","Excited":"IMGexcited.PNG","Inspiration":"IMGinspiration.PNG","Happy":"IMGhappy.PNG"}.get(mood[0][0])
            print(date, m, song[0][0], song[0][1], song[0][3], username, description, song[0][2])
            with connection.cursor() as cursor:
                query = "INSERT INTO calendar (idcalendar, date, mood, song_name, artist, yt, username, description, embed) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (date, m, song[0][0], song[0][1], song[0][3], username, description, song[0][2]))
                connection.commit()
            return render_template('calendar.html')
        return render_template('randomsongforcalendar.html', songs=session['fav'][0], favorite_songs=favorite_songs)
    return render_template('randomsongforcalendar.html', songs=session['fav'][0], favorite_songs=favorite_songs)

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
    if 'refresh' in request.args:
        query = "SELECT mood, why FROM song WHERE song_name = %s"
        songname = session.get('current_song')[0][0]
        with connection.cursor() as cursor:
            cursor.execute(query, (songname,))
            md = cursor.fetchone()
        session['mood'] = md[0]
        session['reason'] = md[1]
        mood = session.get('mood')
        reason = session.get('reason')
        query = "SELECT song_name, artist, embed FROM song WHERE mood = %s AND why = %s ORDER BY RAND() LIMIT 1"
        with connection.cursor() as cursor:
            cursor.execute(query, (mood, reason))
            songs = cursor.fetchall()
            session['current_song'] = songs
    elif session['current_song'] == []:
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
    current_song = session.get('current_song')
    return render_template('randomsong.html', songs=current_song[0], favorite_songs=favorite_songs)

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        
        cursor = connection.cursor(buffered=True)
        cursor.execute('SELECT Song, Artists, yt FROM favorites WHERE username = %s', (username,))
        songs = cursor.fetchall()
        cursor.close()
        return render_template('profile.html', username=username, songs=songs)

@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    if 'username' in session:
        username = session['username']

        cursor = connection.cursor(buffered=True)
        cursor.execute('SELECT * FROM calendar WHERE username = %s', (username,))
        moods = cursor.fetchall()
        cursor.close()
        mood_list = []
        for mood in moods:
            mood_list.append({
                'idcalendar': mood[0],
                'date': mood[1].isoformat(),
                'moodimg': mood[2],
                'song_name': mood[3],
                'artist': mood[4],
                'yt': mood[5],
                'description': mood[7],
                'embed': mood[8]
            })
        return render_template('calendar.html', mood_list=mood_list)
    return redirect(url_for('login'))

@app.route('/mooods', methods=['GET', 'POST'])
def mooods():
    if 'username' in session:
        username = session['username']
        
        cursor = connection.cursor(buffered=True)
        
        cursor.execute('SELECT date FROM calendar WHERE username = %s', (username,))
        day = cursor.fetchall()
        day_list = [{"date": d[0].isoformat()} for d in day]
        
        cursor.execute('SELECT * FROM calendar WHERE username = %s', (username,))
        moods = cursor.fetchall()

        mood_list = [
            {
                'idcalendar': mood[0],
                'date': mood[1].isoformat(),
                'moodimg': mood[2],
                'song_name': mood[3],
                'artist': mood[4],
                'yt': mood[5],
                'description': mood[7],
                'embed': mood[8]
            }
            for mood in moods
        ]

        cursor.close()

        return jsonify({"days": day_list, "moods": mood_list})

    return jsonify({"days": [], "moods": []})

@app.route('/add_mood', methods=['POST'])
def add_mood():
    new_mood = request.get_json()
    date = new_mood['date']
    mood = new_mood['mood']
    song_name = new_mood['song_name']
    artist = new_mood['artist']
    yt = new_mood['yt']
    description = new_mood['description']
    embed = new_mood['embed']
    
    query = 'INSERT INTO calendar (idcalendar, mood, song_name, artist, yt, description, embed) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)'
    with connection.cursor() as cursor:
        cursor.execute(query,(date, mood, song_name, artist, yt, description, embed))
        connection.commit()
    
    return jsonify({'message': 'Event added successfully'}), 201

@app.route('/events')
def events():
    date = request.args.get('date')
    username = session.get('username')
    date = date.split("-")
    date[1] = str(int(date[1]) + 1)
    date = "-".join(date)

    if username:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM calendar WHERE username = %s AND date = %s', (username, date))
        events = cursor.fetchall()
        cursor.close()
        if not events:
            events = None
        return jsonify(events)
    return jsonify([])

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)
