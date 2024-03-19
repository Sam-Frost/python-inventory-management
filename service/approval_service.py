from flask import jsonify
from firebase import get_document_id, read_documents, update_document

from utils import parse_items

from model import assigned_items_model, approval_model

def approval_inventory(data):
    items_dict = parse_items(data['items']) 
    print(data)
    print("-"*20)
    

    if data['action']  == 'Denied':
        parameter = {
            approval_model.emp_id  : data['emp_id'],
            approval_model.employee_name: data['employee'],
            approval_model.call_number: data['callNo'],
            approval_model.tcr_number: data['tcrNo']
        }

        idd = get_document_id(approval_model.table, parameter)
        update_document(approval_model.table, idd, {
            'status' : data['action']
        })
        print("Request sucessfully deined!!!!! YSY!!!!")
        return jsonify({'msg':'Denied!'})
    
    # Check if any item quantiy is less than the assigned quantity
    for key, value in items_dict.items():
        params = {
            assigned_items_model.emp_id :data['emp_id'],
            assigned_items_model.item_name : key
        }
        doc=read_documents(assigned_items_model.table,params)
        id=get_document_id(assigned_items_model.table,params)
        quant=int(doc[0]['quantity'])-int(value)

        if  quant  < 0 :

            print("Quantiy is goinng -ve deined!!!!! YSY!!!!")
            return jsonify({'msg':'Quantity required is more than the assigned quantity@'})
    
    
   
    # Key - item name
    # Value - item quantity
    for key, value in items_dict.items():
        print(key)
        print("-"*20)
        print(value)
        print("-"*20)
        print(data)
        params = {
            assigned_items_model.emp_id :data['emp_id'],
            assigned_items_model.item_name : key
        }
            

        doc=read_documents(assigned_items_model.table,params)
        print(doc)
        id=get_document_id(assigned_items_model.table,params)
        quant=int(doc[0]['quantity'])-int(value)


        update_data={'quantity':quant}
        update_document(assigned_items_model.table,id,update_data)
        
        parameter = {
            'employee_name': data['employee'],
            'call_number': data['callNo'],
            'tcr_number': data['tcrNo']
        }

        idd = get_document_id(approval_model.table, parameter)
        update_document(approval_model.table, idd, {
            'status' : data['action']
        })
   
    return jsonify("all good")