from datetime import datetime
import sqlite3
from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)
app.debug = True
DATABASE_URL = r'.\db\feedback.db'

@app.route('/')
def hello_world():
    return render_template("base.html")

@app.route('/feedback/')
def feedback():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = 'select ROWID,CategoryName from category'
    categories = c.execute(sql).fetchall()
    c.close()
    conn.close()
    return render_template('post.html',categories = categories)

@app.route('/post_feedback/', methods=['POST'])
def post_feedback():
    #如果当前请求的方法为POST
    if request.method == 'POST':
        # 获取表单值
        subject = request.form['subject']
        categoryid = request.form.get('category',1)
        username = request.form.get('username')
        email = request.form.get('email')
        body = request.form.get('body')
        release_time = datetime.now()
        is_processed = 0

        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        sql = "insert into feedback(Subject, CategoryID, UserName, Email, Body, ReleaseTime,IsProcessed) values (?,?,?,?,?,?,?)"
        c.execute(sql,(subject,categoryid,username,email,body,release_time,is_processed))
        conn.commit()
        conn.close()
        return redirect(url_for('feedback'))


@app.route('/admin/list/')
def feedback_list():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = 'select f.ROWID,f.*,c.CategoryName from feedback f INNER JOIN category c ON c.ROWID = f.CategoryID ORDER BY f.ROWID DESC '
    feedbacks = c.execute(sql).fetchall()
    conn.close()
    return render_template('feedback-list.html',items = feedbacks)

@app.route('/admin/feedback/del/<id>')
def delete_feedback(id):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    sql = 'delete from feedback WHERE ROWID = ?'
    c.execute(sql,(id,))
    conn.commit()
    conn.close()
    return redirect(url_for('feedback_list'))


if __name__ == '__main__':
    app.run()
