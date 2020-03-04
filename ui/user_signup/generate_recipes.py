ids = ()
select_rand_recipes = "SELECT * FROM recipes WHERE id IN ?"
#connection = sqlite3.connect('db.sqlite3')

#c = connection.cursor()
#urls_img = c.execute(select_rand_recipe, ids)

#connection.commit()
#connection.close()

def generate_html_page():
    num_days = 7
    with open('user_signup/templates/user_signup/meals.html', 'w') as file:
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
          <section class="jumbotron text-center">
            <div class="container">
              <h1 class="jumbotron-heading">Your Weekly Meals, {{ name }}!</h1>
              <p class="lead text-muted">Your weekly meals have been generated below! You now have the option of either automatically generating your weekly grocery list based on the below recipes by pressing "Generate Grocery List", or you can press "Deselect Recipe" button if you want a new recipe. After deselecting a recipe, a short form will pop up so that you can let us know why you deselected it, we will refrain from showing you this recipe again based on your response.</p>
              <p>
                <button type='submit' class='btn btn-primary btn-lg' onclick=\"window.location.href ='/home/dashboard/meals';\">Generate Grocery List </button><br>
              </p>
            </div>
          </section>

        <div class="container-fluid">
        <div class="row flex-row flex-nowrap">

        """
        file.write(beg_html)

        for i in range(num_days):

            html_body1 = """
            <div class="card-deck">

            <div class="card" style="width: 30rem;">
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
              </ul>

                <a href="#" class="card-link">Recipe link</a>
                <br>
            """
            file.write(html_body2)

            file.write("<button href='/home/deselect?name=button%d' class='btn btn-dark' data-toggle='modal' data-target='#myModal'>Deselect Recipe</button>"% (i+1))
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
