from flask import Flask, jsonify
from flask_caching import Cache <-- 1
import sqlite3

app = Flask(__name__)

# Flask-Caching configuration with Redis
app.config['CACHE_TYPE'] = 'RedisCache' <--- this
app.config['CACHE_REDIS_HOST'] = 'localhost'  # Change if Redis is running elsewhere
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout in seconds <-- this

cache = Cache(app) <-- 2

def get_db_connection():
    conn = sqlite3.connect('database.db')  # Update with your actual database
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/transactions', methods=['GET'])
@cache.cached(timeout=300, key_prefix='transactions_data') <-- 3
def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")  # Update with actual table name
    rows = cursor.fetchall()
    conn.close()
    
    transactions = [dict(row) for row in rows]
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(debug=True)
