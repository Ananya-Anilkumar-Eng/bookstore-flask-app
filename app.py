from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "bookstore_secret"

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- CREATE USERS TABLE ----------
conn = get_db_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")
conn.execute("""
INSERT OR IGNORE INTO users (id, username, password)
VALUES (1, 'admin', 'admin123')
""")
conn.commit()
conn.close()

# ---------- CREATE BOOKS TABLE ----------
conn = get_db_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    price INTEGER
)
""")
conn.execute("""
INSERT OR IGNORE INTO books (id, title, author, price)
VALUES (1, 'Python Basics', 'John Doe', 499)
""")
conn.commit()
conn.close()


# ---------- LOGIN PAGE ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/home")
        else:
            return "Invalid username or password"

    return render_template("login.html")

# ---------- HOME PAGE ----------
@app.route("/home")
def home():
    if "user" in session:
        conn = get_db_connection()
        books = conn.execute("SELECT * FROM books").fetchall()
        conn.close()
        return render_template("home.html", user=session["user"], books=books)
    return redirect("/")

@app.route("/add_book", methods=["POST"])
def add_book():
    if "user" in session:
        title = request.form["title"]
        author = request.form["author"]
        price = request.form["price"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
            (title, author, price)
        )
        conn.commit()
        conn.close()

        return redirect("/home")
    return redirect("/")

@app.route("/delete_book/<int:book_id>")
def delete_book(book_id):
    if "user" in session:
        conn = get_db_connection()
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        conn.close()
        return redirect("/home")
    return redirect("/")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run()
