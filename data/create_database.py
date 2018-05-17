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
c.executescript(sql1)
c.executescript(sql2)
conn.commit()
conn.close()