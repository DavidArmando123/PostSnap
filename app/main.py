# app/main.py
from flask import Blueprint, request, jsonify
from app import db
from app.models import User, posts, comments 
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

main = Blueprint('main', __name__)

@main.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not email or not password or not username:
        return jsonify({"msg": "username, email and password are required"}), 400

    existing_user_by_email = User.query.filter_by(email=email).first()
    if existing_user_by_email:
        return jsonify({"msg": "Email already registered"}), 400

    existing_user_by_username = User.query.filter_by(username=username).first()
    if existing_user_by_username:
        return jsonify({"msg": "Username already taken"}), 400

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully!"}), 201


@main.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", None)
    password = data.get("password", None)

    if not email or not password:
        return jsonify({"msg": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401

    
    if not bcrypt.checkpw(password.encode('utf-8'), user.password): 
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=email, fresh=True)
    return jsonify(access_token=access_token), 200

@main.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 

@main.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify(msg="Logout successful"), 200
