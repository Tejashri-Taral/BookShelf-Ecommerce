import sqlite3

# Path to the database file
DB_NAME = 'data/data.db'

# Function to create the database and tables
def create_tables():
    # Establish a connection to the SQLite database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # SQL queries to create the tables
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    );
    """

    create_books_table = """
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL,
        image TEXT
    );
    """

    create_cart_table = """
    CREATE TABLE IF NOT EXISTS cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(book_id) REFERENCES books(book_id)
    );
    """

    create_purchases_table = """
    CREATE TABLE IF NOT EXISTS purchases (
        purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        FOREIGN KEY(user_id) REFERENCES users(user_id),
        FOREIGN KEY(book_id) REFERENCES books(book_id)
    );
    """

    
    # Execute the SQL commands to create tables
    cursor.execute(create_users_table)
    cursor.execute(create_books_table)
    cursor.execute(create_cart_table)
    cursor.execute(create_purchases_table)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database tables created successfully!")

# Run the function to create tables
if __name__ == '__main__':
    create_tables()
