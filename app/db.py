import sqlite3

DB_NAME = './data/data.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return False  # Username already exists
    
    # If the username does not exist, insert the new user
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True  # Successfully registered


def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_books():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books") 
    books = cursor.fetchall()
    conn.close()
    return books


def add_to_cart(user_id, book_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if the book already exists in the user's cart
    cursor.execute("SELECT * FROM cart WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    existing_item = cursor.fetchone()

    if existing_item:
        # If the book already exists in the cart, update the quantity
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    else:
        # If the book doesn't exist in the cart, add it with quantity 1
        cursor.execute("INSERT INTO cart (user_id, book_id, quantity) VALUES (?, ?, ?)", (user_id, book_id, 1))

    conn.commit()
    conn.close()


def remove_from_cart(user_id, book_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch the current quantity of the book in the user's cart
    cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    current_quantity = cursor.fetchone()
    
    if current_quantity:
        # If the quantity is greater than 1, just decrease the quantity by 1
        if current_quantity['quantity'] > 1:
            cursor.execute("UPDATE cart SET quantity = quantity - 1 WHERE user_id = ? AND book_id = ?", (user_id, book_id))
        else:
            # If quantity is 1, remove the item entirely
            cursor.execute("DELETE FROM cart WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    
    conn.commit()
    conn.close()


def update_purchase_table(user_id, cart_items):
    # Insert the purchased items into the purchase table
    conn = get_connection()
    cursor = conn.cursor()
    
    for item in cart_items:
        cursor.execute('''
            INSERT INTO purchases (user_id, book_id, quantity, total_price)
            VALUES (?, ?, ?, ?)
        ''', (user_id, item['id'], 1, item['price']))  # Assuming quantity is 1 for simplicity
        
    conn.commit()
    conn.close()
    

def get_cart_items(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT books.book_id AS book_id, books.name, books.price, cart.quantity
        FROM cart
        JOIN books ON cart.book_id = books.book_id
        WHERE cart.user_id = ?
    """, (user_id,))
    cart_items = cursor.fetchall()  # This returns a list of sqlite3.Row objects
    conn.close()
    return cart_items


def get_cart_count(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(quantity) FROM cart WHERE user_id = ?", (user_id,))
    cart_count = cursor.fetchone()[0] or 0  # Return 0 if no items are found
    conn.close()
    return cart_count


def checkout(user_id):
    # Example structure: Calculate total price, move to purchases table, clear cart
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(b.price * c.quantity) AS total_price
        FROM cart c
        JOIN books b ON c.book_id = b.book_id
        WHERE c.user_id = ?
    """, (user_id,)) 
    total_price = cursor.fetchone()["total_price"] or 0

    if total_price > 0:
        # Insert items into purchases with individual total price
        cursor.execute("""
            INSERT INTO purchases (user_id, book_id, quantity, total_price)
            SELECT 
                c.user_id, 
                c.book_id, 
                c.quantity, 
                (b.price * c.quantity) AS total_price
            FROM cart c
            JOIN books b ON c.book_id = b.book_id
            WHERE c.user_id = ?
        """, (user_id,))
        # Clear the cart
        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()
    conn.close()
    return total_price

def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries, so you can access columns by name
    return conn
