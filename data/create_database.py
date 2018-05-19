import sqlite3
conn = sqlite3.connect('images.db')
c = conn.cursor()
sql1 = """
DROP TABLE IF EXISTS label;
CREATE TABLE label
(
  id INTEGER PRIMARY KEY,
  name varchar(255)
);
"""
sql2 = """
DROP TABLE IF EXISTS image;
CREATE TABLE image
(
  id INTEGER PRIMARY KEY,
  path varchar(255),
  label_id INTEGER,
  FOREIGN KEY(label_id) REFERENCES label(id)
);
"""
sql3 = """
DROP TABLE IF EXISTS attendance;
CREATE TABLE attendance (
           id integer unique primary key autoincrement,
           userid integer,
           name text,
           cekinout integer(4) not null default (strftime('%s','now'))
);
"""

c.executescript(sql1)
c.executescript(sql2)
c.executescript(sql3)
conn.commit()
conn.close()