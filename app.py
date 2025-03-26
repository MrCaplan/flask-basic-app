from flask import Flask, render_template, request
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]

        new_user = User(name=name, age=age)
        db.session.add(new_user)
        db.session.commit()
        
        return render_template("result.html", name=name, age=age)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)