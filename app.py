import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from email_validator import validate_email,EmailNotValidError


def email_validator_address(email):
    try:
        valid = validate_email(email)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)

def get_db_connection():
      conn = sqlite3.connect('database.db')
      conn.row_factory = sqlite3.Row
      return conn

def get_password(password_id):
    conn = get_db_connection()
    password = conn.execute('SELECT * FROM passwords WHERE id = ?', (password_id,)).fetchone()
    conn.close()
    if password is None:
        abort(404)
    return password


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hussein'

@app.route("/")
def index():
    conn = get_db_connection()
    passwords = conn.execute('SELECT * FROM passwords').fetchall()
    conn.close()
    return render_template('index.html', passwords=passwords)

@app.route("/<int:password_id>")
def password(password_id):
     password = get_password(password_id)
     return render_template('password.html', password=password)



@app.route("/create", methods=("GET", "POST"))
def create():
    
    if request.method == "POST":
        url = request.form["email_URL"]
        email = (request.form["email"])
        email_password = request.form["email_password"]

        if not email:
            flash("email is required")
        else:
            (valid, result) = email_validator_address(email)
            conn = get_db_connection()
            if  valid is True:
                conn.execute(
                    "INSERT INTO passwords (email_URL, email, email_password) VALUES (?, ?, ?)",
                    (url, result, email_password)
                )
        
                conn.commit()
                conn.close()
                return redirect(url_for("index"))
            else:
                flash(result)

    return render_template("create.html")

@app.route('/<int:id>/edit',methods = ('GET', 'POST'))
def edit(id):
    password = get_password(id)
    
    if request.method == 'POST':
        email =(request.form['email'])
        email_password = request.form['email_password']

        if not email:
            flash("email is required")
        else:
            (valid, result) = email_validator_address(email)
            conn = get_db_connection()
            if  valid is True:
                conn.execute("UPDATE passwords SET email = ?, email_password =? WHERE id =?", (result,email_password, id))
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
        
            else:
                flash(result)
    return render_template('edit.html', password=password)

@app.route('/<int:id>/delete',methods = ('GET', 'POST'))
def delete(id):
    password = get_password(id)
    request.method == 'POST'
    conn = get_db_connection()
    conn.execute('DELETE from passwords where id =?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(password['email']))
    return redirect(url_for('index'))

if __name__ == "__main__":
        app.run(debug=True, port=5000)



