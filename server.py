from flask import Flask, request, render_template_string, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'dittis@sunbeam'  # Change to a strong, secure key in production
                                # Required to create a session.

# Database Configuration
db_config = {
    'host': 'localhost',    # Change to you MySQL hostname/ip
    'user': 'appuser',       # Change to your MySQL username
    'password': 'appuser@123', # Change to your MySQL password
    'database': 'productdb'
}

# HTML Templates
login_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    <form method="post" action="/login">
        <p>
        <label for="username">Username:</label>
        <input type="text" name="username" required>
        </p>
        <p>
        <label for="password">Password:</label>
        <input type="password" name="password" required>
        </p>
        <button type="submit">Login</button>
    </form>
</body>
</html>
'''

failed_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Failed</title>
</head>
<body>
    <h2>Login Failed</h2>
    <p>
        Sorry. Invalid email or password.
    </p>
    <p>
        <a href="home">Login Again</a>
    </p>
</body>
</html>
'''

welcome_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
</head>
<body>
    <h2>Welcome, {{ session['username'] }}!</h2>
    <a href="/products">View Products</a> | 
    <a href="/logout">Logout</a>
</body>
</html>
'''

product_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Products</title>
</head>
<body>
    <h2>Products</h2>
    <ul>
        {% for product in products %}
            <li>{{ product[1] }} - Rs. {{ product[3] }}/- : 
            <a href="/delete_product/{{ product[0] }}">Delete</button>
            </a>
            </li>
        {% endfor %}
    </ul>
    <a href="/welcome">Back to Dashboard</a>
</body>
</html>
'''

# Connect to the database
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Home Page
@app.route('/home', methods=['GET'])
def home():
    return render_template_string(login_page)


# Login Route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Vulnerable query (for demonstration purposes)
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    print("Executing SQL:", query)
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        session['username'] = user[1]
        return redirect(url_for('welcome'))
    else:
        return render_template_string(failed_page)


# Welcome Route
@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template_string(welcome_page)

# Products Route
@app.route('/products')
def products():
    if 'username' not in session:
        return redirect(url_for('home'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template_string(product_page, products=products)

# Delete Product Route (Demonstrates SQL Injection vulnerability)
@app.route('/delete_product/<product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    if 'username' not in session:
        return redirect(url_for('home'))

    # Vulnerable query
    query = "DELETE FROM products WHERE id = %s"
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query, (product_id,))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('products'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Run the app
if __name__ == '__main__':
    app.run(port=4000,host='0.0.0.0', debug=True)
