#Importing required packages
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired
import requests
import os

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

#Defining a function to get contents on the desired topic
def get_content(query):
    parameters = {
    "api_key": os.getenv('SPRINGER_API_KEY'),
    "q": query,
    "p": "25"
    }

    response = requests.get(url="https://api.springernature.com/metadata/json", params=parameters)
    response.raise_for_status()

    results = response.json()["records"] #Getting hold of desired results

    content_list = [] #Creating a list to get hold of the contents

    for result in results:
        new_value = {
            "title": result.get("title"),
            "authors": ', '.join([author.get("creator") for author in result.get("creators")]),
            "url": result.get("url")[0].get("value"),
            "abstract": result.get("abstract"),
            "publication name": result.get("publicationName"),
            "publisher": result.get("publisher"),
            "publication date": result.get("publicationDate"),
            "publication type": result.get("publicationType"),
            "copyright": result.get("copyright"),
            "openaccess": result.get("openaccess"),
            "subjects": ', '.join(result.get("subjects"))
        }

        content_list.append(new_value)
    
    return content_list #Returning the list for further use

#Creating a global variable to store content
content_list = []

#Creating a form
class Form(FlaskForm):
    topic = StringField(label="", validators=[DataRequired()], render_kw={"placeholder": "Topic you are interested in..."})
    search = SubmitField(label="Search", validators=[DataRequired()])

#Creating a flask app
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv('APP_SECRET_KEY') #You can create a random one. e,g 'bvcdrtghnk'

#Creating bootstrap for styling
bootstrap = Bootstrap5(app=app)

#Defining web pages
@app.route("/", methods=["POST","GET"])
def home():
    form = Form()
    if form.validate_on_submit():
        global content_list
        content_list = get_content(query=form.topic.data)
        return render_template("index.html", form=form, data=content_list, topic=form.topic.data)
    
    return render_template("index.html", form=form, data=None)

@app.route("/info/<title>")
def show_info(title):
    global content_list
    for content in content_list:
        if content.get("title") == title:
            information = content
    return render_template("info.html", info=information)

#Running flask app
if __name__ == "__main__":
    app.run(debug=True)
