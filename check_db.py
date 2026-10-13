import sqlite3
conn = sqlite3.connect('database/pdf_index.db')
cursor = conn.cursor()

print('=== Checking Database ===')

# Check total pages with Revenue
cursor.execute("SELECT COUNT(*) FROM pdf_content WHERE content LIKE '%Revenue%' OR content LIKE '%revenue%'")
print('Total pages with Revenue:', cursor.fetchone()[0])

# Check by file
cursor.execute('''SELECT p.filename, COUNT(*) as cnt 
FROM pdf_content pc 
JOIN pdfs p ON pc.pdf_id = p.id 
WHERE pc.content LIKE '%Revenue%' OR pc.content LIKE '%revenue%' 
GROUP BY p.filename''')
print('By file:', cursor.fetchall())

# Try FTS5 search
try:
    cursor.execute('SELECT COUNT(*) FROM pdf_content WHERE pdf_content MATCH "Revenue*"')
    print('FTS5 results:', cursor.fetchone()[0])
except Exception as e:
    print('FTS5 error:', e)

conn.close()