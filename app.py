import os
import sqlite3
import json
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('select id, date, cost, share, person from data order by id desc')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries, data=json.dumps([tuple(row) for row in entries]))

@app.route('/add', methods=['POST'])
def addCost():
    db = get_db()
    if request.method == 'POST':
        curNew = db.cursor()
        dataFields = ['date', 'class', 'location', 'detail', 'cost', 'share', 'person']
        dataValues = [request.form['date'],
                      request.form['class'],
                      request.form['location'],
                      request.form['comment'],
                      request.form['cost'],
                      request.form['share'],
                      request.form['user']]
        query = 'INSERT INTO data (%s) VALUES (%s)' % (
            ', '.join(dataFields),
            ', '.join(['?'] * len(dataValues))
        )
        curNew.execute(query, dataValues)
        db.commit()
        curNew.close()
        flash('New entry saved')
    else:
        error = 'Invalid post'
    # refresh results
    # cur = db.execute('select date, cost, person from data order by index desc')
    # entries = cur.fetchall()
    return redirect(url_for('index'))#render_template('index.html', entries=entries)

@app.route('/query', methods=['GET'])
def getSummary():
    return 'get summary of costs'

@app.route('/detail/<id>', methods=['GET', 'POST'])
def detailPage(id):
    db = get_db()
    cur = db.execute('select * from data where id = ?', [id])
    entry = cur.fetchall()
    cur.close()
    # print(entry[0]['id'])
    return render_template('details.html', entries=entry)

@app.route('/change', methods=['POST'])
def changeOneEntry():
    db = get_db()
    if request.method == 'POST':
        curNew = db.cursor()
        dataFields = ['date', 'class', 'location', 'detail', 'cost', 'share', 'person']
        dataValues = [request.form['date'],
                      request.form['class'],
                      request.form['location'],
                      request.form['comment'],
                      request.form['cost'],
                      request.form['share'],
                      request.form['user'],
                      request.form['id']]
        # print(dataValues)
        query = 'UPDATE data SET %s WHERE %s' % (
            '=?, '.join(dataFields) + '=?',
            'id=?'
        )
        curNew.execute(query, dataValues)
        db.commit()
        curNew.close()
        flash('Entry updated')
    else:
        error = 'Invalid post'
    # refresh results
    # cur = db.execute('select date, cost, person from data order by index desc')
    # entries = cur.fetchall()
    return redirect(url_for('index'))#render_template('index.html', entries=entries)

@app.route('/delete/<id>', methods=['GET','POST'])
def deleteEntry(id):
    db = get_db()
    cur = db.cursor()
    cur = db.execute('delete from data where id = ?', [id])
    db.commit()
    cur.close()
    flash('Entry deleted!')
    return redirect(url_for('index'))

@app.route('/summary')
def displaySummary():
    db = get_db()
    cur = db.execute('select id, date, cost, share, person from data order by id desc')
    entries = cur.fetchall()
    return render_template('summary.html', data=json.dumps([tuple(row) for row in entries]))


# database
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database.db'),
    SECRET_KEY='development key',
    # USERNAME='admin',
    # PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
