

def query_recipes(recipe_ids):
    connection = sqlite3.connect('db.sqlite3')
    c = connection.cursor()
    sql_recipes = "SELECT * FROM recipes WHERE recipe_id = ?"
    c.execute(sql_recipes, (recipe_ids,))
    recipes = c.fetchall()
    return recipes
