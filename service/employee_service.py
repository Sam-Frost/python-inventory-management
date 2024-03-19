from flask import jsonify, session
from firebase import create_document, get_document_by_id, read_documents, update_document

from model import employee_model, variables_model

import consts

def  register_employee(data):

    for key, value in data.items():
        data[key] = value.strip()

    if employee_exists(data['phone']):
        return jsonify({'message': 'User already exists'})
    
    name =  data['first_name']+ " " + data['last_name']

    # logic to create my  custom empoyee_id

    emp_id = generate_emp_id()

    if not emp_id:
        return jsonify({'message':"Error creating user!"})

    employee_data = {   
        employee_model.emp_id :  emp_id,
        employee_model.employee_name : name,
        employee_model.phone : data['phone'],
        employee_model.position : data['position'],
        employee_model.password: data['password']
    }

    if create_document(employee_model.table, employee_data):
        return jsonify({'message': "Employee Added!"})
    else :
        return jsonify({'message':"Error creating user!"})
    

def employee_exists(phone):

    params = {
        employee_model.phone : phone
    } 

    if read_documents(employee_model.table,params):
        return True
    
    return False

def generate_emp_id():

    if session['location'] == 'gurgaon':
        
        doc = get_document_by_id(variables_model.table, consts.GURGAON_EMPLOYEE_COUNT)
        updated_quantity = int(doc[variables_model.emp_id_gurgaon]) + 1
        param = {
            variables_model.emp_id_gurgaon : updated_quantity
        }
        update_document(variables_model.table, consts.GURGAON_EMPLOYEE_COUNT, param)
        emp_id = 'ggn-' + str(updated_quantity)

    elif session['location'] == 'faridabad':

        doc = get_document_by_id(variables_model.table, consts.FARIDABAD_EMPLOYEE_COUNT)
        updated_quantity = int(doc[variables_model.emp_id_faridabad]) + 1
        param = {
            variables_model.emp_id_faridabad : updated_quantity
        }
        update_document(variables_model.table, consts.FARIDABAD_EMPLOYEE_COUNT, param)
        emp_id = 'far-' + str(updated_quantity)

    else :
        return None

    return emp_id