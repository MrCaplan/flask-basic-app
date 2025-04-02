from flask import Flask, render_template, request, redirect, jsonify
from models import db, User
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

app = Flask(__name__)

# DB 연결 설정
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT 설정
app.config['JWT_SECRET_KEY'] = "my-super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

# 초기화
jwt = JWTManager(app)
db.init_app(app)

with app.app_context():
    db.create_all()

# 회원가입 페이지
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        name = request.form["name"]
        age = request.form["age"]

        if not username or not password or not name or not age:
            return render_template("register.html", error="모든 필드를 입력해주세요")

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="이미 존재하는 사용자입니다")

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, name=name, age=age)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

# 로그인 페이지
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return render_template("login.html", error="잘못된 사용자 정보입니다")

        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)
        return render_template("profile.html", current_user=user.username, token=access_token)

    return render_template("login.html")

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = make_response(redirect("/login"))
    unset_jwt_cookies(response)
    response.set_cookie("access_token", "", expires=0)
    response.set_cookie("refresh_token", "", expires=0)
    return response


# 프로필 페이지
@app.route("/profile")
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    return render_template("profile.html", current_user=current_user)

# REST API - 사용자 전체 목록
@app.route("/api/users", methods=["GET"])
def get_users():
    users = User.query.all()
    result = [{"id": user.id, "name": user.name, "age": user.age} for user in users]
    return jsonify(result)

# REST API - 사용자 등록 (JSON)
@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data.get("name")
    age = data.get("age")

    if not name or not age:
        return jsonify({"error": "이름과 나이를 모두 입력해주세요."}), 400

    new_user = User(name=name, age=age)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "사용자 등록 완료!", "user_id": new_user.id}), 201

# REST API - 토큰 재발급
@app.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200

@app.route("/")
def home():
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
