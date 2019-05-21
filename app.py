from flask import Flask
import os
import sqlite3
from flask import render_template, redirect, g, request, session, url_for, abort, flash



DATABASE = r'X:\PycharmProjects\Flasker\tmp\flasker.db'
SECRET_KEY = '123456'

app = Flask(__name__)
# app.config.from_envvar('FLASK_SETTINGS', slice=True)
app.config.from_object(__name__)

def connect_db():
    '''连接我们配置好的数据库'''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    '''返回现在数据库连接，如果没有连接，现在连接到数据库并返回'''
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db



@app.teardown_appcontext
def close_db(error):
    '''在项目结束的时候，关闭我们的数据库连接'''
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/add_entry',methods=['POST'])
def add_entry():
    '''添加文章接口'''
    if session.get('logged_in',None):
        title = request.form.get('title')
        article = request.form.get('text')
        #存入数据库
        g.db.execute("insert into entried(title,text) VALUES (?,?)"
                     ,[title,article])
        g.db.commit()
        flash("add an entry in SQL")
        return redirect(url_for('show_entries'))
    else:
        abort(401)

@app.route('/')
def show_entries():
    cur = g.db.execute("select title,text from entried order by id desc")
    entries = [dict(title = row[0],text = row[1])for row in cur.fetchall()]
    return render_template('show_entries.html',entries=entries)

@app.route('/login',methods=['GET','POST'])
def login():
    # if request.args #GET方法
    error = None
    if request.form.get('username') != 'gaopeng':
        error = "Invaild username"
    elif request.form.get('password') != 'gaopeng':
        error = 'Invaild password'
    else: #登陆成功
        session['logged_in'] = True
        flash('You has login successfully')
        return redirect(url_for('show_entries'))
    return render_template('login.html',error=error)

@app.route('/logout')
def logout():
    '''退出的逻辑'''
    session.pop('logged_in',None)
    flash('you have logout successfully')
    return redirect(url_for('show_entries'))

@app.before_request
def brfore_request():
    g.db = get_db()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == '__main__':
    app.run()
