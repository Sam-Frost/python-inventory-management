from datetime import timedelta
from flask import jsonify
from firebase import create_document, read_documents, read_documents_startswith
from model import employee_model, assigned_items_model, approval_model

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from utils import location_from_emp_id

def login(data):
    phone = data['phone']
    password = data['password']

    params = {
        employee_model.phone : phone,
        employee_model.password : password
    }

    user_data = read_documents(employee_model.table , params)

    if user_data :
        
        location = location_from_emp_id(user_data[0][employee_model.emp_id])

        info = {
            "emp_id": user_data[0][employee_model.emp_id],
            'location': location
        }

        access_token = create_access_token(identity=info, expires_delta=timedelta(hours=12))

        response = {
            "success": True,
            "message": "Login successful",
            "user": user_data[0],
            "access_token": access_token
        }
    else:
        response = {'login': 'unsuccess'}

    return jsonify(response)

def profile(current_user):
    params = {
        employee_model.emp_id : current_user[employee_model.emp_id]
    }
    print(current_user[employee_model.emp_id])
    data = read_documents(employee_model.table, params)
    return data[0]

def assigned_item(current_user):

    params = {
        employee_model.emp_id : current_user['emp_id']
    }

    assigned_item = read_documents(assigned_items_model.table, params)

    for items in assigned_item:
        delete_field(items, "emp_id")

    if assigned_item:
        return jsonify({"assigned_items": assigned_item})
    else:
        return jsonify({'Error': 'Could not load Item'})

def get_orders(current_user):
    
    params = {
        employee_model.emp_id : current_user['emp_id']
    }
    doc = read_documents(approval_model.table, params)

    for item in doc:
        delete_field(item, "tcr_number")
        delete_field(item, "user_doc_id")
        delete_field(item, "employee_name")
        delete_field(item, "customer_name")
        delete_field(item, "call_number")

    return jsonify(doc)

def save_orders(current_user, request_data):
    try:
        date = request_data['date']
        tcr_number = request_data['tcr_number']
        call_number = request_data['call_number']
        customer_name = request_data['customer_name']
        employee_name = request_data['employee_name']
        items = request_data['items']
        total_price = int(request_data['total_price'])
        request_no = request_data['request_no']
        status = request_data['status']
        brand = request_data['brand']

        order_data = {
            approval_model.emp_id: current_user['emp_id'],
            approval_model.date: date,
            approval_model.tcr_number: tcr_number,
            approval_model.call_number: call_number,
            approval_model.customer_name: customer_name,
            approval_model.employee_name: employee_name,
            approval_model.items: items,
            approval_model.total_price: total_price,
            approval_model.request_no: request_no,
            approval_model.status: status,
            approval_model.brand: brand
        }

        create_document(approval_model.table, order_data)

        # Dummy response
        response_data = {
            "status": "success",
            "message": "Request Sent Successfully",
            "request_no": request_no
        }

        return jsonify(response_data)
    except:
        error_data = {
            "status": "failure",
            "message": "Error Occurred",
            "request_no": request_no
        }
        return jsonify(error_data)
    

def approved_requests(current_user):

    params = {
        employee_model.emp_id : current_user[employee_model.emp_id]
    }

    doc = read_documents(approval_model.table, params)
    filtered_doc = []

    # Iterate through the list of dictionaries
    for item in doc:
        # Check if the status is not 'Pending'
        if item.get('status') != 'Pending':
            # If the status is not 'Pending', add the item to the new list
            filtered_doc.append(item)

    return jsonify(filtered_doc)



def delete_field(dictionary, field_name):
    if field_name in dictionary:
        del dictionary[field_name]
        return True
    else:
        return False
