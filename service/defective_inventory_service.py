from flask import jsonify, redirect, session, url_for

from firebase import create_document, get_document_by_id, get_document_id, read_documents, update_document

from model import employee_model, item_model, defective_items_model, assigned_items_model
from utils import get_emp_id

def add_defective_inventory(data):
    
    for key, value in data.items():
        data[key] = value.strip()

    if check_phone_number_name_match(data['employee_phone'], data['employee_name']) and check_item_name_part_number_match(data['item_name'], data['part_no']):
        
        emp_id = get_emp_id(data['employee_name'])
        
        create_document( defective_items_model.table, {
            defective_items_model.item_name: data['item_name'],
            defective_items_model.part_number: data['part_no'],
            defective_items_model.quantity: data['quantity'],
            defective_items_model.employee_name:data['employee_name'] ,
            defective_items_model.emp_id : emp_id,
            defective_items_model.call_number: data['call_number'],
            defective_items_model.date : data['formatted_date'],  # Save the returned date
            'status' : 'pending'
        })

        params = {
            assigned_items_model.emp_id: emp_id,
            assigned_items_model.part_number: data['part_no']
        }

        doc_id = get_document_id(assigned_items_model.table, params)

        doc = read_documents(assigned_items_model.table, params)[0]

        updated_quantity = int(doc[assigned_items_model.quantity]) - int(data['quantity'])

        if updated_quantity < 0:
            return jsonify({"msg": "Quantity is less than the assigned quantity!"})

        updated_data = {
            assigned_items_model.quantity : updated_quantity
        }

        update_document(assigned_items_model.table, doc_id, updated_data)


        return jsonify({"msg": "Return Accepted!"})
    else :
        return jsonify({"msg": "(Phone Number and Employee Name) or )Item Name and Part number)doesn't match!"})            
    

def write_off(data):
    # Get data from the request form
        item_name = data['itemName']
        part_no = data['partNo']
        quantity = data['quantity']
        emp_id= data['emp_id']
        date = data['date']

        param = {
            defective_items_model.emp_id : emp_id,
            defective_items_model.item_name : item_name,
            defective_items_model.quantity : quantity,
            defective_items_model.date : date,
            defective_items_model.part_number : part_no
        }

        docid=get_document_id(defective_items_model.table, param)
        data={
            'status':'write_off'
        }
        update_document(defective_items_model.table,docid,data)
        return redirect(url_for('defective_list'))

def  send_to_vendor(data):

    item_name = data['itemName']
    part_no = data['partNo']
    quantity = data['quantity']
    emp_id= data['emp_id']
    date = data['date']

    param = {
            defective_items_model.emp_id : emp_id,
            defective_items_model.item_name : item_name,
            defective_items_model.quantity : quantity,
            defective_items_model.date : date,
            defective_items_model.part_number : part_no
    }
    docid=get_document_id(defective_items_model.table,param)
    data={
        'status':'send_to_vendor'
    }
    update_document(defective_items_model.table,docid,data)
    return redirect(url_for('defective_list'))    

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


