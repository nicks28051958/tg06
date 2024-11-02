import sqlite3
import os

db_path = 'F:\\STUDENT_PYTHON\\TG06\\tg06\\user.db'
conn = sqlite3.connect(db_path)
print("Database created at:", os.path.abspath(db_path))

cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT
)
''')
conn.commit()
conn.close()
import os

print(os.listdir('F:\\STUDENT_PYTHON\\TG06\\tg06'))
