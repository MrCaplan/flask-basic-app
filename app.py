from flask import Flask, render_template, request
from models import db, User
from flask import jsonify
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://postgres:mypassword@localhost:5432/flask_db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "my-super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

jwt = JWTManager(app)
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

@app.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({"id": user.id, "name": user.name, "age": user.age})
    return jsonify(result)

@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    print("request content type:", request.content_type)
    print("request data:", request.data)
    print("request json:", request.get_json())
    name = data.get("name")
    age = data.get("age")

    if not name or not age:
        return jsonify({"error": "이름과 나이를 모두 입력해주세요."}), 400
    
    new_user = User(name=name, age=age)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "사용자 등록 완료!", "user_id": new_user.id}), 201

@app.route("/login", methods=["POST"])
def login():
    print("/login 요청 도착!")
    print("Headers:", request.headers)
    print("Data:", request.get_data())

    data = request.get_json()
    print("Parsed JSON:", data)
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "잘못된 사용자 정보입니다."}), 401
    
    access_token = create_access_token(identity=user.username)
    refresh_token = create_refresh_token(identity=user.username)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    return jsonify({"msg": f"{current_user}님 환영합니다!"})
    
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    name = data.get("name")
    age = data.get("age")

    # 필수 값 누락 시
    if not username or not password or not name or not age:
        return jsonify({"error": "모든 필드를 입력해주세요"}), 400
    
    # 중복 사용자 방지 
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "이미 존재하는 사용자입니다"}), 409
    
    hashed_pw = generate_password_hash(password)
    
    new_user = User(username=username, password=hashed_pw, name=name, age=age)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "회원가입 성공!"}), 201

@app.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)