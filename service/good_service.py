from flask import jsonify, session
from firebase import create_document, get_document_id, read_documents, update_document
from model import good_return_model, item_model, employee_model
from utils import get_emp_id

def add_good_return(data):

    for key, value in data.items():
        data[key] = value.strip()


    if check_phone_number_name_match(data['phone'], data['name']) and check_item_name_part_number_match(data['item_name'], data['part_no']):
        
        param = {
            item_model.item_name : data['item_name'],
            item_model.part_number : data['part_no'],
            item_model.location : session['location']
        }
        # Retrieve the existing item document
        doc = read_documents(item_model.table, param)

        # Update the quantity with the new quantity
        new_quantity = int(data['quantity']) + int(doc[0]['quantity'])
        doc_id = get_document_id(item_model.table, param)

        # Update the quantity in the database
        update_data = {
            'quantity': new_quantity
        }
        update_document(item_model.table, doc_id, update_data)

        # Create a new document in the 'good_return' collection
        good_return_data = {
            good_return_model.emp_id : get_emp_id(data['name']),
            good_return_model.item_name: data['item_name'],
            good_return_model.part_number : data['part_no'],
            good_return_model.quantity: int(data['quantity']),
            good_return_model.employee_name: data['name'],
            good_return_model.date: data['date']
        }
        create_document(good_return_model.table, good_return_data)
        return jsonify({"msg": "Return Accepted!"})    
    
    else:
        return jsonify({"msg": "(Phone Number and Employee Name) or (Item Name and Part number) doesn't match!"})
    

def check_phone_number_name_match(phone_number, name):
    print("check_phone_number_name_match function called!")
    params = {
       employee_model.phone  : phone_number,
       employee_model.employee_name : name
    }

    # NOT CHECKING LOCATION FOR EMPLOYEE, SINCE ADMIN GURGAON KA GURGAON HE BETHA HAI, to employee bhi gurgaon ka hi hoga
    if read_documents(employee_model.table, params):
        return True
    
    return False
    
def check_item_name_part_number_match(item_name, part_no):
    print("check_item_name_part_number_match called!")

    params = {
       item_model.item_name : item_name,
       item_model.part_number : part_no,
       item_model.location : session['location']
    }
    if read_documents(item_model.table, params):
        return True
    
    return False
