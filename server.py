
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response,url_for

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
with engine.connect() as conn:
    delete_table_command="""
    DROP TABLE test;
    """
    res = conn.execute(text(delete_table_command))
    
    create_table_command = """
    CREATE TABLE IF NOT EXISTS test (
    id serial,
    name text
    )
    """
    res = conn.execute(text(create_table_command))
    insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
    res = conn.execute(text(insert_table_command))
    conn.commit()
    # you need to commit for create, insert, update queries to reflect
with engine.connect() as conn:
    cursor = conn.execute(text("select * FROM recipe_rl_include where user_id =77"))
    record = cursor.fetchone()
    second_record = cursor.fetchone()
    #print(record)
    for row in cursor:
        print (list(row))


from flask import Flask
from flask import session


app = Flask(__name__)

app.secret_key = 'bikefan'

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

@app.route('/', methods=["POST", "GET"])
def home():
    recipes = []
    if request.method == "POST":
        #rint(request.form["type"] )
        if request.form["type"] == 'email':
            email = request.form["email"]

            emails = []
            select_query = "SELECT user_id from Users where email = :email"
            cursor = g.conn.execute(text(select_query), {'email': email})
            
            for result in cursor:
                emails.append(result[0])
                
                # print(result)
            cursor.close()
            context = dict(data = emails)
            # print(context)
            if len(context['data']) == 0:
                print('email not exist')
            else:
                session['id'] = context['data'][0]
                session['user_email'] = email
                print(session['id'])
        elif request.form["type"] == 'search':
            recipe_name = request.form["recipe_name"]
            select_query = "select  * from Recipes where lower(recipe_name) like :recipe_name"
            cursor = g.conn.execute(text(select_query), {'recipe_name': '%' + recipe_name.lower() + '%'})

            for result in cursor:
                dict_ = {'recipe_id':result[0], 'recipe_name':result[1], 'cooking_time':result[2], 'cooking_difficulty':result[3], 'descriptions':result[4], 'author_id':result[5]}
                recipes.append(dict_)
            cursor.close()
            # print(recipes)
        elif request.form["type"] == 'upload':
            if session.get("id",'') != '':
                recipe_n = request.form['recipe_name']
                #author_id = request.form['author_id']
                cooking_time = request.form['cooking_time']
                cooking_difficulty = request.form['cooking_difficulty']
                descriptions = request.form['descriptions']

                params = {}
                params["recipe_name"] =recipe_n
                params["author_id"] =session.get("id",'')
                params["cooking_time"] =cooking_time
                params["cooking_difficulty"] =cooking_difficulty 
                params["descriptions"] =descriptions
                #print(**params)
                sql_command = text("""
                INSERT INTO Recipes (recipe_name, author_id, cooking_time, cooking_difficulty, descriptions)
                VALUES (:recipe_name, :author_id, :cooking_time, :cooking_difficulty, :descriptions)
                """)
                g.conn.execute(sql_command, params)
                g.conn.commit()
        elif request.form["type"] == 'add':
            print("here ")
            recipe_list = []
            # Corrected the SQL command and added a placeholder for the parameter.
            sql_command = text("""
            SELECT rl_name FROM Recipe_lists WHERE user_id = :user_id
            """)
            cursor = g.conn.execute(sql_command, {'user_id': session['id']})
            print(session['id'])
            for row in cursor:
                recipe_list.append(row[0])  # Assuming 'rl_name' is the column name you're interested in.
            cursor.close()  # Close the cursor after use.
            
            #print(recipe_list)
            if len(recipe_list)==0:
                return "you don't have recipe_list "
            else:
                recipe_list_contain = {"user_id":session['id'],"rl_name":recipe_list[0],"recipe_id":request.form["recipe_id"]}
                print(recipe_list_contain)
                sql_command = text("""
            INSERT INTO recipe_rl_include(user_id,rl_name,recipe_id) VALUES(:user_id,:rl_name,:recipe_id)
            """)
            cursor = g.conn.execute(sql_command,recipe_list_contain)
            g.conn.commit()
            cursor.close()
    
        elif request.form["type"] == 'rate':
            user_id = session.get('id', '')
            if user_id != '':
                recipe_id = request.form["recipe_id"]
                rate = request.form["rate"]
                print('params',user_id,recipe_id,rate)

                select_query = "SELECT * from rating where user_id = :user_id and recipe_id = :recipe_id"
                cursor = g.conn.execute(text(select_query), {'user_id':user_id, 'recipe_id':recipe_id})
                results = cursor.fetchall() 
                length = len(results)
                print('length', length)

                if length == 0:
                    sql_command = """
                    INSERT INTO rating 
                    VALUES (:user_id, :recipe_id, :rate)
                    """
                    g.conn.execute(text(sql_command),{'user_id':user_id, 'recipe_id':recipe_id,'rate':rate})
                    g.conn.commit()
                else:
                    sql_command = """
                    UPDATE rating 
                    SET rating_score = :rate 
                    WHERE user_id = :user_id AND recipe_id = :recipe_id
                    """
                    g.conn.execute(text(sql_command),{'user_id':user_id, 'recipe_id':recipe_id,'rate':rate})
                    g.conn.commit()
        elif request.form["type"] == 'follow':
            user_id = session.get('id', '')

            if user_id != '':
                author_id = request.form["author_id"]

                select_query = "SELECT * from follow where followee_id = :author_id and follower_id = :user_id"
                cursor = g.conn.execute(text(select_query), {'author_id':author_id, 'user_id':user_id})
                results = cursor.fetchall() 
                length = len(results)

                if length == 0:
                    sql_command = """
                        INSERT INTO follow 
                        VALUES (:author_id, :user_id)
                        """
                    g.conn.execute(text(sql_command),{'author_id':author_id, 'user_id':user_id})
                    g.conn.commit()
    
    user = session.get('user_email', '')
    return render_template("home.html", user_name = user, recipes = recipes)

from flask import request, g
from sqlalchemy import text

@app.route("/search", methods=["POST", "GET"])
def search():

    if request.method == "POST":
        if request.form["type"] == 'search':
            Things = request.form["ingredients"].split(',') + request.form["tools"].split(',')
            placeholders = ', '.join([f':Things{i}' for i in range(len(Things))])
            print(Things)
            # Using named parameters in the query to prevent SQL injection
            select_query = text(''' 
                                select Recipes.*
                                from
                                    (select recipe_id, count(distinct thing) as num
                                    from
                                        ((select made_of as recipe_id, I_name as thing
                                        from made_of)
                                        union all
                                        (select recipe_id, tool_name as thing
                                        from require)) U
                                    where thing in ({})
                                    group by recipe_id
                                    having count(distinct thing) > 0
                                    ) C
                                    join
                                    Recipes
                                    on C.recipe_id = Recipes.recipe_id
                                order by num desc
                                limit 3
                                '''.format(placeholders))
            params = {f'Things{i}': Things[i] for i in range(len(Things))}
            # Executing the query with parameters
            cursor = g.conn.execute(select_query, params)
            recipes = []
            for result in cursor:
                dict_ = {'recipe_id':result[0], 'recipe_name':result[1], 'cooking_time':result[2], 'cooking_difficulty':result[3], 'descriptions':result[4], 'author_id':result[5]}
                recipes.append(dict_)
            cursor.close()
            #print(final_results)


            # Assuming you have some follow-up logic to display these recipes
            # For example, return a template with the recipes
            user = session.get('user_email', '')
            return render_template("Fancy_search.html", recipes=recipes,user_name = user)
        
        if request.form["type"] == 'follow':
            user_id = session.get('id', '')
            if user_id != '':
                author_id = request.form["author_id"]

                select_query = "SELECT * from follow where followee_id = :author_id and follower_id = :user_id"
                cursor = g.conn.execute(text(select_query), {'author_id':author_id, 'user_id':user_id})
                results = cursor.fetchall() 
                length = len(results)

                if length == 0:
                    sql_command = """
                        INSERT INTO follow 
                        VALUES (:author_id, :user_id)
                        """
                    g.conn.execute(text(sql_command),{'author_id':author_id, 'user_id':user_id})
                    g.conn.commit()

        
    user = session.get('user_email', '')
    # If the request method is not POST, or for any other logic you might have
    # for example, showing the search page if the method is GET
    return render_template("Fancy_search.html",user_name = user)
        





@app.route("/<name>")
def user(name):
    return f"Hello {name}!"

@app.route("/rate", methods=["POST", "GET"])
def rate():
    id = request.form["recipe_id"]
    rate = request.form["rate"]
    print('id', id)
    return f"rate {id} {rate}!"

@app.route("/dislike", methods=["POST", "GET"])
def dislike():
    id = request.form["recipe_id"]
    print('dislike ', id)
    return f"dislike {id}!"

@app.route("/login")
def login():
    user = session.get('user_email', '')
    return render_template("login.html", user_name = user)

@app.route("/recommend")
def recommed():
    recipes = []
    id = session.get('id', '')
    if id != '':
        select_query = ''' select Recipes.recipe_id,Recipes.recipe_name,Recipes.cooking_time,Recipes.cooking_difficulty,Recipes.descriptions,Recipes.author_id
                            from
                            (select 
                            recipe_id
                            from
                            (select I_name, action 
                            from relationship 
                            where user_id = :user_id) R
                            join
                            (select 
                            made_of as recipe_id,
                            I_name
                            from made_of) M
                            on R.I_name = M.I_name
                            group by recipe_id
                            having count(case when action = 'dislike' then 1 else null end) = 0
                            order by count(case when action = 'like' then 1 else null end) desc
                            limit 3) recipe_like
                            join Recipes
                            on recipe_like.recipe_id = Recipes.recipe_id
                            left join rating
                            on recipe_like.recipe_id = rating.recipe_id
                            group by Recipes.recipe_id,Recipes.recipe_name,Recipes.cooking_time,Recipes.cooking_difficulty,Recipes.descriptions,Recipes.author_id
                            order by avg(case when rating_score is not null then rating_score else 0 end) desc
                        '''
        cursor = g.conn.execute(text(select_query), {'user_id': id}) 
        for result in cursor:
            dict_ = {'recipe_id':result[0], 'recipe_name':result[1], 'cooking_time':result[2], 'cooking_difficulty':result[3], 'descriptions':result[4], 'author_id':result[5]}
            recipes.append(dict_)
        cursor.close()
        if len(recipes) == 0:
            select_query = ''' select Recipes.*
                                from
                                (select recipe_id 
                                from rating
                                where recipe_id not in 
                                (select recipe_id
                                from
                                    (select I_name
                                    from relationship 
                                    where user_id = :user_id
                                    and action = 'dislike') R
                                    join
                                    (select 
                                    made_of as recipe_id,
                                    I_name
                                    from made_of) M
                                    on R.I_name = M.I_name
                                ) 
                                group by recipe_id 
                                order by avg(rating_score) desc 
                                limit 3) R
                                join Recipes
                                on R.recipe_id = Recipes.recipe_id
                            '''


            cursor2 = g.conn.execute(text(select_query), {'user_id': id}) 
            for result in cursor2:
                dict_ = {'recipe_id':result[0], 'recipe_name':result[1], 'cooking_time':result[2], 'cooking_difficulty':result[3], 'descriptions':result[4], 'author_id':result[5]}
                recipes.append(dict_)

    else:
        select_query = ''' select Recipes.*
                            from
                            (select recipe_id 
                            from rating 
                            group by recipe_id 
                            order by avg(rating_score) desc 
                            limit 3) R
                            join Recipes
                            on R.recipe_id = Recipes.recipe_id
                        '''
        cursor = g.conn.execute(text(select_query))
        for result in cursor:
            dict_ = {'recipe_id':result[0], 'recipe_name':result[1], 'cooking_time':result[2], 'cooking_difficulty':result[3], 'descriptions':result[4], 'author_id':result[5]}
            recipes.append(dict_)
        cursor.close()

    user = session.get('user_email', '')
    return render_template("recommend.html", user_name = user, recipes = recipes)

@app.route("/profile", methods=["POST", "GET"])
def profile():
    if session.get("id",'') == '':
        return f"Please log in to see this page!"
    
    if request.method == "POST":
        if request.form["type"] == 'delete':
            print('delete')
            recipe_id = request.form["recipe_id"]
            delete_command = '''
                                Delete FROM Recipes where recipe_id = :recipe_id
                            '''
            g.conn.execute(text(delete_command), {'recipe_id': recipe_id})
            g.conn.commit()
        elif request.form["type"] == 'add_ingredient_like':
            id = session.get('id', '')
            I_name = request.form["I_name"]

            select_query = "SELECT * from relationship where user_id = :user_id and I_name = :I_name and action = 'like'"
            cursor = g.conn.execute(text(select_query), {'user_id':id, 'I_name':I_name})
            results = cursor.fetchall() 
            length = len(results)
            cursor.close()

            select_query = "SELECT * from Ingredients where I_name = :I_name"
            cursor = g.conn.execute(text(select_query), {'I_name':I_name})
            results = cursor.fetchall() 
            length2 = len(results)
            cursor.close()


            if length == 0 and length2 != 0:
                sql_command = '''
                                    INSERT INTO relationship
                                    VALUES (:user_id, :I_name, 'like')
                                '''
                g.conn.execute(text(sql_command), {'user_id':id, 'I_name':I_name})
                g.conn.commit()
        elif request.form["type"] == 'add_ingredient_dislike':
            id = session.get('id', '')
            I_name = request.form["I_name"]

            select_query = "SELECT * from relationship where user_id = :user_id and I_name = :I_name and action = 'dislike'"
            cursor = g.conn.execute(text(select_query), {'user_id':id, 'I_name':I_name})
            results = cursor.fetchall() 
            length = len(results)
            cursor.close()

            select_query = "SELECT * from Ingredients where I_name = :I_name"
            cursor = g.conn.execute(text(select_query), {'I_name':I_name})
            results = cursor.fetchall() 
            length2 = len(results)
            cursor.close()

            if length == 0 and length2 != 0:
                sql_command = '''
                                    INSERT INTO relationship
                                    VALUES (:user_id, :I_name, 'dislike')
                                '''
                g.conn.execute(text(sql_command), {'user_id':id, 'I_name':I_name})
                g.conn.commit()
        elif request.form["type"] == 'add_tool':
            id = session.get('id', '')
            T_name = request.form["tool"]

            select_query = "SELECT * from own where user_id = :user_id and tool_name = :T_name"
            cursor = g.conn.execute(text(select_query), {'user_id':id, 'T_name':T_name})
            results = cursor.fetchall() 
            length = len(results)
            cursor.close()

            select_query = "SELECT * from Cooking_tools where tool_name = :T_name"
            cursor = g.conn.execute(text(select_query), {'T_name':T_name})
            results = cursor.fetchall() 
            length2 = len(results)
            cursor.close()

            if length == 0 and length2 != 0:
                sql_command = '''
                                    INSERT INTO own
                                    VALUES (:user_id, :T_name)
                                '''
                g.conn.execute(text(sql_command), {'user_id':id, 'T_name':T_name})
                g.conn.commit()
        
        
    id = session.get('id', '')
    recipes = []
    ingredients_like = []
    ingredients_dislike = []
    tools = []
    followers = []
    followees = []
    rates = []
    if id != '':
        select_query = '''  select *
                            from
                            Recipes
                            where author_id = :author_id
                            '''
        cursor = g.conn.execute(text(select_query),{'author_id': id})
        for result in cursor:
            dict_ = {'recipe_id':result[0], 'recipe_name':result[1], 'cooking_time':result[2], 'cooking_difficulty':result[3], 'descriptions':result[4], 'author_id':result[5]}
            recipes.append(dict_)
        print('recipes',recipes)
        cursor.close()


        select_query = '''  select I_name
                            from
                            relationship
                            where user_id = :user_id
                            and action = 'like'
                            '''
        cursor = g.conn.execute(text(select_query),{'user_id': id})
        for result in cursor:
            ingredients_like.append(result[0])
        cursor.close()

        select_query = '''  select I_name
                            from
                            relationship
                            where user_id = :user_id
                            and action = 'dislike'
                            '''
        cursor = g.conn.execute(text(select_query),{'user_id': id})
        for result in cursor:
            ingredients_dislike.append(result[0])
        cursor.close()

        select_query = '''  select tool_name
                            from
                            own
                            where user_id = :user_id
                            '''
        cursor = g.conn.execute(text(select_query),{'user_id': id})
        for result in cursor:
            tools.append(result[0])
        cursor.close()

        select_query = '''  select follower_id
                            from
                            follow
                            where followee_id = :user_id
                            '''
        cursor = g.conn.execute(text(select_query),{'user_id': id})
        for result in cursor:
            followers.append(result[0])
        cursor.close()

        
        select_query = '''  select followee_id
                            from
                            follow
                            where follower_id = :user_id
                            '''
        cursor = g.conn.execute(text(select_query),{'user_id': id})
        for result in cursor:
            followees.append(result[0])
        cursor.close()

        select_query = '''  select recipe_name, rating_score
                            from
                            (select recipe_id, rating_score
                            from
                            rating
                            where user_id = :user_id) R
                            join Recipes 
                            on R.recipe_id = Recipes.recipe_id
                            '''
        cursor = g.conn.execute(text(select_query),{'user_id': id})
        for result in cursor:
            rates.append({'name':result[0], 'score':result[1]})
        cursor.close()

    user = session.get('user_email', '')
    return  render_template("profile.html", user_name = user, recipes = recipes, ingredients_like=ingredients_like, ingredients_dislike = ingredients_dislike, tools =tools, followers = followers, followees = followees,rates=rates)

if __name__ == "__main__":
    app.run()

