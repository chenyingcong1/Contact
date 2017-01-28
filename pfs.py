from datetime import datetime
import sqlite3
import os
from flask import Flask,render_template,request,redirect,url_for,g,flash

app = Flask(__name__)
app.debug = True
app.secret_key = "asdbfhjrrwre"
DATABASE_URL = r'.\db\feedback.db'
UPLOAD_FOLDER = r'.\uploads'
ALLOWED_EXTENSIONS = ['.jpg','.png','.gif']

#检查文件是否允许上传
def allowed_file(filename):
    #
    _,ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


#将游标获取的tuple根据数据库列表转换为dict
def make_dicts(cursor,row):
    return dict((cursor.description[i][0],value) for i,value in enumerate(row))

#获取（建立数据库连接）
def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE_URL)
        db.row_factory = make_dicts
    return db
#执行sql语句不返回数据结果
def execute_sql(sql,prms=()):
    c = get_db().cursor()
    c.execute(sql,prms)
    c.connection.commit()
#执行用于选择数据的sql语句
def query_sql(sql,prms =(),one=False):
    c = get_db().cursor()
    result = c.execute(sql,prms).fetchall()
    c.close()
    return (result[0] if result else None) if one else result

#关闭连接（在当前app上下文销毁时关闭连接）
@app.teardown_appcontext
def close_connection(exeption):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()
@app.route('/')
def hello_world():
    return render_template("base.html")

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        sql = 'select count(*) AS [Count] from UserInfo WHERE UserName=? and Password=?'
        result = query_sql(sql,(username,pwd),one=True)
        if int(result.get('Count')) > 0:
            return redirect(url_for('feedback_list'))
        flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/feedback/')
def feedback():
    sql = 'select ROWID,CategoryName from category'
    categories = query_sql(sql)
    return render_template('post.html',categories = categories)
@app.route('/post_feedback/', methods=['POST'])
def post_feedback():
    if request.method == 'POST':
        subject = request.form['subject']
        categoryid = request.form.get('category',1)
        username = request.form.get('username')
        email = request.form.get('email')
        body = request.form.get('body')
        release_time = datetime.now()
        is_processed = 0
        img_path = None
        if 'image' in request.files:
            img = request.files['image']
            if allowed_file(img.filename) == True:
                img_path = datetime.now().strftime('%Y%m%d%H%M%f') + os.path.splitext(img.filename)[1]
                img.save(os.path.join(UPLOAD_FOLDER,img_path))


        sql = "insert into feedback(Subject, CategoryID, UserName, Email, Body, ReleaseTime,IsProcessed,Image) values (?,?,?,?,?,?,?,?)"
        execute_sql(sql,(subject,categoryid,username,email,body,release_time,is_processed,img_path))
        return redirect(url_for('feedback'))
@app.route('/admin/list/')
def feedback_list():
    key = request.args.get('key','')
    sql = 'select f.ROWID,f.*,c.CategoryName from feedback f INNER JOIN category c ON c.ROWID = f.CategoryID WHERE f.Subject LIKE ? ORDER BY f.ROWID DESC '
    feedbacks = query_sql(sql,('%{}%'.format(key),))
    return render_template('feedback-list.html', items=feedbacks,key=key)
@app.route('/admin/edit/<id>/')
def edit_feedback(id=None):
    sql = 'select ROWID,CategoryName from category'
    categories = query_sql(sql)
    sql = 'select rowid,* from feedback WHERE rowid = ?'
    current_feedback = query_sql(sql,(id,),one=True)
    return render_template('edit.html',categories = categories, item = current_feedback)

@app.route('/admin/save_edit/',methods=['POST'])
def save_feedback():
    if request.method == 'POST':
        # 获取表单值
        rowid = request.form.get('rowid',None)
        subject = request.form['subject']
        categoryid = request.form.get('category', 1)
        username = request.form.get('username')
        email = request.form.get('email')
        body = request.form.get('body')
        reply = request.form.get('reply')
        release_time = request.form.get('releasetime')
        is_processed =1 if request.form.get('isprocessed',0) == 'on' else 0

        sql = """update feedback set
                              Subject = ?,
                              CategoryID = ?,
                              UserName = ?,
                              Email = ?,
                              Body = ?,
                              Reply = ?,
                              ReleaseTime = ?,
                              IsProcessed = ?
                      WHERE rowid = ?

        """
        execute_sql(sql,(subject, categoryid, username, email, body, reply,release_time, is_processed,rowid))
        return redirect(url_for('feedback_list'))
@app.route('/admin/feedback/del/<id>')
def delete_feedback(id):
    sql = 'delete from feedback WHERE ROWID = ?'
    execute_sql(sql,(id,))
    return redirect(url_for('feedback_list'))
if __name__ == '__main__':
    app.run()
