import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session,flash
from db import get_books, add_to_cart, get_cart_items, checkout, register_user, authenticate_user, remove_from_cart, get_connection
app = Flask(__name__)
app = Flask(__name__, static_folder='static', static_url_path='/static')

app.secret_key = 'your_secret_key'  # For session management

@app.route('/')
def home():
    books = get_books()  # Fetch the list of books from the database
    return render_template('index.html', books=books)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Register the user in the database
        if register_user(username, password):
            return redirect(url_for('login'))
        else:
            return 'Username already exists', 400  # Optionally handle username conflict
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Authenticate the user
        if authenticate_user(username, password):
            session['user_id'] = username  # Store user session
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials', 400  # Optionally handle invalid login
    return render_template('login.html')

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart_route(book_id):
    if 'user_id' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    # Add book to cart (with handling if book already exists in cart)
    add_to_cart(user_id, book_id)
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:book_id>')
def remove_from_cart_route(book_id):
    if 'user_id' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    # Call remove_from_cart function from db.py to remove the item from the cart
    remove_from_cart(user_id, book_id)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    import sqlite3
    if 'user_id' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Get cart items with their total price (price * quantity)
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.book_id, b.name, b.price, c.quantity, (b.price * c.quantity) AS total_price
        FROM cart c
        JOIN books b ON c.book_id = b.book_id
        WHERE c.user_id = ?
    """, (user_id,))

    cart_items = cursor.fetchall()

    # Calculate the overall total price for the cart
    overall_total_price = sum(item['total_price'] for item in cart_items)

    conn.close()

    return render_template('cart.html', cart_items=cart_items, total_price=overall_total_price)

@app.route('/checkout')
def checkout_route():
    if 'user_id' not in session:  # Ensure user is logged in
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Get the items in the cart along with the total price
    cart_items = get_cart_items(user_id)  # This now returns both items and total price
    
    if not cart_items:  # If the cart is empty, don't allow checkout
        flash("Your cart is empty, add items before checking out.", "warning")
        return redirect(url_for('cart'))  # Redirect to cart if empty
    
    total_price = checkout(user_id)  # Function updates the purchases table and clears the cart
    
    flash(f"Checkout successful! Total price: ${total_price:.2f}", "success")
    
    # Redirect to a page where the user can see their order summary or home page
    return redirect(url_for('home'))  # You can redirect to the home page or another page


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user session
    return redirect(url_for('home'))  # Redirect to the home page after logout

if __name__ == '__main__':
    app.run(debug=True)
