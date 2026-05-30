#!/usr/bin/env python3
"""Sync local question_bank to Render PostgreSQL"""
import sys, os, psycopg2

def sync():
    target_url = os.environ.get('DATABASE_URL', '')
    if not target_url:
        print('ERROR: Set DATABASE_URL env var (from Render dashboard)')
        print('Example: set DATABASE_URL=postgres://user:pass@host:5432/dbname')
        return
    
    print('Connecting to local DB...')
    local = psycopg2.connect(host='localhost', dbname='question_bank', user='postgres', password='')
    lcur = local.cursor()
    lcur.execute('SELECT COUNT(*) FROM questions')
    local_count = lcur.fetchone()[0]
    print(f'Local questions: {local_count}')
    
    print('Connecting to target DB...')
    target = psycopg2.connect(target_url)
    tcur = target.cursor()
    
    # Get columns
    lcur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'questions' ORDER BY ordinal_position")
    cols = [c[0] for c in lcur.fetchall()]
    col_list = ', '.join('"' + c + '"' for c in cols)
    placeholders = ', '.join(['%s'] * len(cols))
    
    # Create table
    print('Creating questions table...')
    tcur.execute('DROP TABLE IF EXISTS questions CASCADE')
    col_defs = ', '.join('"' + c + '" TEXT' for c in cols)
    tcur.execute('CREATE TABLE questions (' + col_defs + ')')
    tcur.execute('CREATE TABLE IF NOT EXISTS student_progress (id SERIAL PRIMARY KEY, student_name TEXT, question_id INTEGER, student_answer TEXT, status TEXT, score FLOAT, max_score INTEGER, created_at TIMESTAMP DEFAULT NOW())')
    
    # Copy data in batches
    lcur.execute('SELECT ' + col_list + ' FROM questions ORDER BY id')
    batch = []
    count = 0
    for row in lcur:
        batch.append(tuple(str(v) if v is not None else None for v in row))
        if len(batch) >= 100:
            sql = 'INSERT INTO questions (' + col_list + ') VALUES (' + placeholders + ')'
            for r in batch:
                tcur.execute(sql, r)
            target.commit()
            count += len(batch)
            print(f'  Synced {count}/{local_count}...')
            batch = []
    if batch:
        sql = 'INSERT INTO questions (' + col_list + ') VALUES (' + placeholders + ')'
        for r in batch:
            tcur.execute(sql, r)
        target.commit()
        count += len(batch)
    
    tcur.execute('SELECT COUNT(*) FROM questions')
    target_count = tcur.fetchone()[0]
    local.close()
    target.close()
    print(f'DONE: {target_count} questions synced!')

if __name__ == '__main__':
    sync()