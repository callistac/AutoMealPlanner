import sqlite3
import re

def generate_html_page(filename, recipes):
    ids = ()
    rec_ids = [x[0] for x in recipes]
    rec_ids = tuple(rec_ids)
    print("IDSSSS", rec_ids)

    num_days = len(recipes)
    with open('user_signup/templates/user_signup/'+filename, 'w') as file:
        beg_html = """
        {% extends 'base.html' %}

        {% block body %}
        <html>
        <head>
        <title>meals</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
        </head>
        <body>
        """
        file.write(beg_html)
        description_html = """
          <section class="jumbotron text-center">
            <div class="container">
              <h1 class="jumbotron-heading">%s, {{ user }}!</h1>
              <p class="lead text-muted"> %s </p>
            <button type="button" value='Download' onclick="window.location.href = '/home/dashboard/meals/download/';" class='btn btn-primary btn-lg' > Generate Grocery List</button><br>
            </div>
          </section>

        <div class="container-fluid">
        <div class="row flex-row flex-nowrap">
        """
        header_new_meals = "Your weekly meals have been generated below! \
        You now have the option of either automatically generating your weekly grocery \
        list based on the below recipes by pressing \"Generate Grocery List\", or you can press \"Deselect Recipe\" \
        button if you want a new recipe. After deselecting a recipe, a short form will pop up so that \
        you can let us know why you deselected it, we will refrain from showing you this recipe again based on your response.\
        If you would like to deselect all 7 recipes, refresh the page."

        header_old_meals = "Your past meals have been generated. Select generate grocery list to regenerate your grocery list from last week.\
        If you would like to rate a recipe from last week to help us better learn what you like, please click \"Rate Recipe\" below the recipe."

        if filename == 'past_meals.html':
            file.write(description_html % ('Your Past Meals', header_old_meals))
        else:
            file.write(description_html % ('Your Weekly Meals', header_new_meals))

        for i in range(num_days):
            html_body1 = """
            <div class="card-deck">

            <div class="card" style="width: 30rem;">
              <img class="card-img-top" src=%s alt="Card image cap">
            <div class="card-body">
            <h5 class='card-title'>%s, Day %d </h5>

            <p class="card-text">%s Servings</p>
            </div>
              <ul class="list-group list-group-flush">

              </ul>
              <p class="align-items-center">
                <a href=%s class="card-link">Link to recipe</a>
                <br>
              </p>
            """
            file.write(html_body1 % (recipes[i][3], recipes[i][1], (i+1), recipes[i][4], recipes[i][2]))
            if filename == 'past_meals.html':
                file.write("<button href='/home/rating?name=%s' class='btn btn-success' data-toggle='modal' data-target='#myModal'>Rate Recipe</button>"% (rec_ids[i]))
            else:
                file.write("<button href='/home/deselect?name=%s' class='btn btn-dark' data-toggle='modal' data-target='#myModal'>Deselect Recipe</button>"% (rec_ids[i]))
            html_body3 = """
                <br>
            </div>
              <!-- Modal -->
              <div class="modal fade" id="myModal" role="dialog">
                <div class="modal-dialog">

                  <!-- Modal content-->
                  <div class="modal-content">
                    <form action="" method="post">
                    {% csrf_token %}
                    <div class="modal-header">
                        <h3 class="modal-title" id="exampleModalLabel">Please share why you are deselecting this recipe.</h3>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                          <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                        {% for field in form %}
                              <label>{{ field.label_tag }}</label>
                              <div class="col">{{ field }}</div>
                        {% endfor %}
                        </div>
                      <br><br>
                      <button type="submit" class="btn btn-dark">Submit</button>
                    </div>
                    </form>
                  </div>

              </div>
              </div>
            </div>

            <br><br><br>

            """
            file.write(html_body3)

        end_html = """

        </div>
        </div>
        </body>
        </html>
        {% endblock %}
        """
        file.write(end_html)
        file.close()
