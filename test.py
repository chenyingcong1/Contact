import sqlite3
id = 6
DB_Feedback = r'.\db\feedback.db'
conn = sqlite3.connect(DB_Feedback)
c = conn.cursor()
sql = 'select CategoryName from category'
categories = c.execute(sql).fetchall()

sql = 'select * from feedback WHERE ROWID = ?'
current_feedback = c.execute(sql,(id,)).fetchone()
item = current_feedback
c.close()
conn.close()
print(categories)
print(current_feedback)
print(item[0])