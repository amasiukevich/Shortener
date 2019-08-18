from flask import Flask, render_template, flash, request, redirect
from wtforms import TextField, Form
from wtforms.validators import DataRequired
from random import randint
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = '62f23675912c5f48fcb40dcb0ba4dbf61c7cdd6e'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"

db = SQLAlchemy(app)

class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    shortened_url = db.Column(db.String(30), unique=True, nullable=False)
    original_url = db.Column(db.String(), unique=True, nullable=False) 

    def __repr__(self):
        return f"{self.item_id} | {self.shortened_url} | {self.original_url}"


class UrlForm(Form):

    url = TextField('Shorten your url:  ', validators=[DataRequired()])

def get_short_urls():
    return [item.shortened_url for item in Item.query.all()]

def get_original_urls():
    return [item.original_url for item in Item.query.all()]


def shorten(url):

    shortened_urls = get_short_urls()
    original_urls = get_original_urls()
    # checks if url is in database
    if url not in original_urls:
        candidate_url = ""
        while True:
            candidate_url = make_new_url()
            if candidate_url not in shortened_urls:
                break

        new_item = Item(shortened_url=candidate_url, original_url=url)
        db.session.add(new_item)
        db.session.commit()
        return candidate_url
    # if record exists
    else:
        return Item.query.filter_by(original_url=url).first().shortened_url
            

def make_new_url():
    final_url_base = "http://localhost:5000/"
    url = ""
    # randomly generate 7-character url
    rand_choice = -1
    for i in range(7):
        rand_choice = randint(0, 2)
        cort = [randint(48, 57), randint(65, 90), randint(97, 122)]
        url += chr(cort[rand_choice])
    
    url = final_url_base + url
    return url


@app.route('/', methods=['GET', 'POST'])
def hello():
    form = UrlForm(request.form)
    print(form.errors)

    db.create_all()

    if request.method == 'POST':
        url = request.form['url']
        print(url)

    if form.validate():
        flash(f'This is your shortened url: {shorten(url)}')
    else:
        flash('All the fields are required')

    return render_template('urls.html', form=form)

@app.route("/<string>")
def main_fict(string):
    shortened = "http://localhost:5000/" + string 
    if shortened in get_short_urls():
        return redirect(Item.query.filter_by(shortened_url=shortened).first().original_url)
    else:
        error = "404, Your url doesn't exist"
        return render_template('error.html', error=error)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080)