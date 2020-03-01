ids = ()
select_rand_recipes = "SELECT recipe_pic, recipe_link FROM recipes WHERE recipe_id IN ?"
#connection = sqlite3.connect('db.sqlite3')

#c = connection.cursor()
#urls_img = c.execute(select_rand_recipe, ids)

#connection.commit()
#connection.close()


num_weeks = 7
with open('meals.html', 'w') as file:
    beg_html = """
    {% extends 'base.html' %}

    {% block body %}
    <html>
    <head>
    <title>meals</title>
    </head>
    <body>
      <section class="jumbotron text-center">
        <div class="container">
          <h1 class="jumbotron-heading">Your Weekly Meals</h1>
          <p class="lead text-muted">Your weekly meals have been generated below! You now have the option of either automatically generating your weekly grocery list based on the below recipes by pressing "Generate Grocery List", or you can press "Deselect Recipe" button if you want a new recipe. After deselecting a recipe, a short form will pop up so that you can let us know why you deselected it, we will refrain from showing you this recipe again based on your response.</p>
          <p>
            <button type='submit' class='btn btn-primary' onclick=\"window.location.href ='/home/dashboard/meals';\">Generate Grocery List </button><br>
          </p>
        </div>
      </section>

    <div class="container-fluid">
    <div class="row flex-row flex-nowrap">

    """
    file.write(beg_html)

    for i in range(num_weeks):

        html_body1 = """
        <div class="card-deck">

        <div class="card" style="width: 18rem;">
          <img class="card-img-top" src='https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fimages.media-allrecipes.com%2Fuserphotos%2F20969.jpg' alt="Card image cap">
        <div class="card-body">
        """
        file.write(html_body1)
        file.write("<h5 class='card-title'>Name of Recipe, Day %d </h5>" % (i+1))
        html_body2 = """
        <p class="card-text">Any information we might want to include.</p>
        </div>
          <ul class="list-group list-group-flush">
            <li class="list-group-item">Cras justo odio</li>
            <li class="list-group-item">Dapibus ac facilisis in</li>
            <li class="list-group-item">Vestibulum at eros</li>
          </ul>
          <div class="card-body">
            <button type='submit' class='btn btn-dark' onclick=\"window.location.href ='/home/dashboard/meals';\">Deselect Recipe</button><br>\n
            <br>
            <a href="#" class="card-link">Card link</a>
            <a href="#" class="card-link">Another link</a>
          </div>
        </div>
        </div>
        <br><br><br>

        """
        file.write(html_body2)
        '''
        file.write("<h2>Day %d</h2>\n" % (i+1))
        file.write("<img src='https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fimages.media-allrecipes.com%2Fuserphotos%2F20969.jpg'>\n")
        #file.write("<img src= %s >\n" % (url_img[i]))

        file.write("<button type='submit' class='btn btn-dark' onclick=\"window.location.href ='/home/dashboard/meals';\">Deselect</button><br>\n")
        file.write("<br>\n")
        '''
    end_html = """

    </div>
    </div>
    </body>
    </html>
    {% endblock %}
    """
    #file.write("<br><h4>If everything looks good to you, generate your weekly grocery list by clicking the below button!</h4>")
    #file.write("<br><button type='submit' class='btn btn-primary' onclick=\"window.location.href ='/home/dashboard/meals';\">Generate Grocery List </button><br><br>\n")
    file.write(end_html)
