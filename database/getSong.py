from flask import Flask, render_template, request, redirect, url_for, flash, session
from DB import get_db_connection
import pymysql
import os
pymysql.install_as_MySQLdb()
connection = get_db_connection()

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
app = Flask(__name__, template_folder=template_dir,static_folder=static_dir)
app.secret_key = 'your_secret_key'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/sign_up')
def signup():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM username")
        username = cursor.fetchall()
    return render_template('signup.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM username WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

        if user:
            session['username'] = username
            return redirect(url_for('select_mood'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/sign_up', methods=['POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO username (username, email, password) VALUES (%s, %s, %s)", (username, email,password))
            connection.commit()

        return redirect(url_for('signup'))

@app.route('/select_mood')
def select_mood():
    return render_template('feel.html')

@app.route('/sad', methods=['GET', 'POST'])
def sad():
    return render_template('sad.html')

@app.route('/happy', methods=['GET', 'POST'])
def happy():
    return render_template('happy.html')

@app.route('/randomsong')
def randomsong():
    mood = request.args.get('mood')
    why = request.args.get('why')

    query = "SELECT song_name, Artist, Embed FROM song WHERE mood = %s AND why = %s ORDER BY RAND() LIMIT 1"
    with connection.cursor() as cursor:
        cursor.execute(query, (mood, why))
        songs = cursor.fetchall()
    return render_template('randomsong.html', songs=songs)

@app.route('/exited', methods=['GET', 'POST'])
def exited():
    return render_template('exited.html')

@app.route('/inspiration', methods=['GET', 'POST'])
def inspiration():
    return render_template('inspiration.html')

@app.route('/anger', methods=['GET', 'POST'])
def anger():
    return render_template('anger.html')

@app.route('/song')
def song():
    return render_template('song.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
