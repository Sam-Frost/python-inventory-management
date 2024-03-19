from flask import Blueprint, jsonify, request, session
from firebase import create_document, read_documents
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from service import api_service

api = Blueprint('api', __name__)

@api.route('/login', methods=['POST'])
def login():
    print("Login route called!")
    # Get email and password from the request
    data = request.json
    return api_service.login(data)


@api.route('/profile')
@jwt_required()
def profile():
    print("Profile route called!")
    current_user = get_jwt_identity()
    return api_service.profile(current_user)


@api.route('/items_assigned', methods=['GET'])
@jwt_required()
def assigned_item():
    print("Items assigned route called!")
    current_user = get_jwt_identity()
    return api_service.assigned_item(current_user)
  


@api.route('/orders', methods=['GET', 'POST'])
@jwt_required()
def submit_order():
    print("Orders route called!")
    current_user = get_jwt_identity()
    if request.method == "GET":
        return api_service.get_orders(current_user)
    else:
        # Get request body
        request_data = request.json
        return api_service.save_orders(current_user, request_data)


@api.route('/approved_requests', methods=['GET'])
@jwt_required()
def get_approved_requests():
    print("Approved requests route called!")
    current_user = get_jwt_identity()
    return  api_service.approved_requests(current_user)





