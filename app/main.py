from flask import Blueprint, request, jsonify
from flask_login import current_user 
from app import db
import os
from werkzeug.utils import secure_filename
from app.models import User, posts, comments 
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    return jsonify({
        "logged_in_as": current_user_email,
        "user_id": user.id,
        "username": user.username
    }), 200

@main.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify(msg="Logout successful"), 200


from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

@main.route("/add_post", methods=["POST"])
@jwt_required()
def add_post():
    if "image" not in request.files:
        return jsonify({"msg": "No image part"}), 400
    
    image = request.files["image"]
    content = request.form.get("content")
    
    if not content:
        return jsonify({"msg": "Content is required"}), 400
    
    if image.filename == "":
        return jsonify({"msg": "No selected file"}), 400
    
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
        img_url = f"/{image_path}"
    else:
        return jsonify({"msg": "Invalid file type"}), 400

    user_id = get_jwt_identity()
    
    new_post = posts(content=content, img_url=img_url, user_id=user_id)  
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({"msg": "Post created successfully!", "post": {"content": content, "img_url": img_url}}), 201
