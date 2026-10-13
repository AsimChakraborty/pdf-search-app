with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def search_pdfs(query, limit=1000):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    query = query.strip()
    words = query.split()
    
    if len(words) == 1:
        search_query = f'"{words[0]}"*'
    else:
        search_conditions = []
        for word in words:
            word = word.strip()
            if word:
                search_conditions.append(f'"{word}"*')
        search_query = ' OR '.join(search_conditions)'''

new = '''def search_pdfs(query, limit=1000):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    query = query.strip()
    words = query.split()
    
    # Build case-insensitive search
    search_conditions = []
    for word in words:
        word = word.strip()
        if word:
            lower_word = word.lower()
            upper_word = word.upper()
            if lower_word != upper_word:
                search_conditions.append(f'"{lower_word}"* OR "{upper_word}"*')
            else:
                search_conditions.append(f'"{word}"*')
    
    if len(search_conditions) == 1:
        search_query = search_conditions[0]
    else:
        search_query = ' OR '.join(search_conditions)'''

content = content.replace(old, new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')