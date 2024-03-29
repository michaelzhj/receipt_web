import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

try:
    
    tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

except NameError:
    # Fallback for interactive environments like Jupyter notebooks
    # Manually specify the path to your 'templates' directory here
    tmpl_dir = os.path.join(os.getcwd(), 'templates')
    
#app = Flask(__name__, template_folder=tmpl_dir)

DATABASE_USERNAME = "hz2906"
DATABASE_PASSWRD = "763092Kgb!"
DATABASE_HOST = "35.212.75.104" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"
engine = create_engine(DATABASEURI)



from flask import Flask

app = Flask(__name__)

@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None
@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/<name>")
def user(name):
    return f"Hello {name}!"

@app.route('/home')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)
    #
    # example of a database query
    #
    names = []
    select_query = "SELECT name from test"
    cursor = g.conn.execute(text(select_query))
    for result in cursor:
        names.append(result[0])
    cursor.close()


    context = dict(data = names)


    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(port=5001,debug=True)