import sqlite3
import sys
import logging
from flask import Flask, jsonify, json, make_response, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime

# global variable for logger
logger: logging.Logger = logging.getLogger(__name__)

# Function to get a database connection.


def get_db_connection():
    try:
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        app.config['dbConnectionCount'] += 1
        return connection
    except:
        logger.error('Error getting connection!')

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['dbConnectionCount'] = 0

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger.error('Article Not Found!')
        return render_template('404.html'), 404
    else:
        title = dict(post)['title']
        logger.debug(f'Article {title} retrieved!')
        return render_template('post.html', post=post)

# Define the About Us page


@ app.route('/about')
def about():
    logger.debug('Navigating to about us page!')
    return render_template('about.html')

# Define the post creation functionality


@ app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            logger.debug(f'New article {title} created')

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthz page


@ app.route('/healthz')
def health():
    data = {'result': 'OK - healthy'}
    return make_response(jsonify(data), 200)

# Define the metrics page


@ app.route('/metrics')
def metrics():
    data = get_matrics_data()
    return make_response(data, 200)


def get_matrics_data():
    connection = get_db_connection()

    postCount = len(connection.execute(
        'SELECT * FROM posts').fetchall())
    connection.close()

    data = {'db_connection_count': app.config['dbConnectionCount'],
            'post_count': postCount
            }
    return jsonify(data)


def setup_logger():
    file_handler = logging.FileHandler("app.log")  # file handler

    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    handlers = [file_handler, stderr_handler, stdout_handler]

    logging.basicConfig(handlers=handlers,
                        format="%(asctime)8s %(levelname)-10s %(message)s")
    logger.setLevel(logging.DEBUG)


    # start the application on port 3111
if __name__ == "__main__":
    setup_logger()
    app.run(host='0.0.0.0', port='3111', debug=True)
