import sqlite3

conn = sqlite3.connect('database/pdf_index.db')
cursor = conn.cursor()

print('Rebuilding FTS5 index...')

# Drop and recreate the FTS5 virtual table
cursor.execute('DROP TABLE IF EXISTS pdf_content')

# Recreate with FTS5
cursor.execute('''
CREATE VIRTUAL TABLE pdf_content USING fts5(
    content,
    content='pdf_content_legacy',
    content_rowid='rowid'
)
''')

# Wait, that's not right. Let me check the table structure first
cursor.execute(\"SELECT sql FROM sqlite_master WHERE type='table' AND name LIKE '%pdf_content%'\")
for row in cursor.fetchall():
    print(row[0])

conn.close()
