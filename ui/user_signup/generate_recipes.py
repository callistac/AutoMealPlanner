

def generate_html_page(recipes):
    num_days = len(recipes)
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
                <form action='SaveResults/' method='POST'>
                {% csrf_token %}
                <button type='submit' class='btn btn-primary btn-lg'> Generate Grocery List</button><br>
                </form>
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
              <img class="card-img-top" src=%s alt="Card image cap">
            <div class="card-body">
            <h5 class='card-title'>%s, Day %d </h5>

            <p class="card-text">Any information we might want to include.</p>
            </div>
              <ul class="list-group list-group-flush">
                <li class="list-group-item">Cras justo odio</li>
                <li class="list-group-item">Dapibus ac facilisis in</li>
              </ul>
              <p>
                <a href=%s class="card-link">Link to recipe</a>
                <br>
              </p>
            """
            file.write(html_body1 % (recipes[i][2], recipes[i][0], (i+1), recipes[i][1]))
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
