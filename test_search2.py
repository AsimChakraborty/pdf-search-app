import sqlite3

conn = sqlite3.connect('database/pdf_index.db')
cursor = conn.cursor()

# Check all pages in update.pdf
cursor.execute('''SELECT page_number, content FROM pdf_content 
WHERE pdf_id = (SELECT id FROM pdfs WHERE filename = 'update.pdf')
ORDER BY page_number''')

pages = cursor.fetchall()
print(f'Total pages in update.pdf: {len(pages)}')

# Check which pages contain 'revenue' (case insensitive)
for page_num, content in pages:
    if 'revenue' in content.lower():
        print(f'  Page {page_num}: contains revenue')

# Check FTS5 index
cursor.execute("SELECT COUNT(*) FROM pdf_content WHERE pdf_content MATCH 'revenue*'")
print(f'FTS5 (lowercase): {cursor.fetchone()[0]}')

cursor.execute("SELECT COUNT(*) FROM pdf_content WHERE pdf_content MATCH 'Revenue*'")
print(f'FTS5 (uppercase): {cursor.fetchone()[0]}')

conn.close()