from flask import jsonify, session
from firebase import create_document, read_documents, update_document, get_document_id

from model import item_model, assigned_items_loan_nos_model, assigned_items_model
from utils import get_emp_id

def add_item(data):

    for key, value in data.items():
        data[key] = value.strip()

    if item_exists(data['part_number']):
        return jsonify({'status': 'exists'})

    # If item does not exist, add it to the collection
    item_data = {
        item_model.item_name: data['item_name'],
        item_model.part_number: data['part_number'],
        item_model.quantity: int(data['quantity']),
        item_model.price: float(data['price']),
        item_model.location: session['location']
    }

    # Save the data to Firebase
    create_document(item_model.table, item_data)
    return jsonify({'status': 'Successfully Added Item!'}) 

def update_item(item_data):

    # Getting the increment value
    update_quantity=int(item_data['quantity'])

    params = {
    item_model.part_number : item_data['part_number'],
    item_model.location : session['location']
    }

    # Getting current quantity
    document_id = get_document_id(item_model.table, params)
   
    temp=read_documents(item_model.table, params)


    # Increasing the quantity
    update_quantity+=int(temp[0]['quantity'])

    # Updating the new quantity in firebase
    data = {item_model.quantity: update_quantity} 
    return update_document(item_model.table, document_id, data)
def assign_item(data):
    try:
        for item in data:
            # PART 1 - Decrease Total Inventory
            item_name = item['itemName']
            item_quantity = item['quantity']
            part_number = item['partNumber']

            param = {
                item_model.part_number : part_number,
                item_model.location : session['location']
            }
            doc = read_documents(item_model.table, param)
            id = get_document_id(item_model.table, param)

            # Decreasing the quantity from total inventory 
            quant = int(doc[0]['quantity']) - int(item_quantity)

            # Updating the items table with decreased quantity
            data = {'quantity': quant}
            update_document(item_model.table, id, data)

            # PART 2 - Store data for loan number
            print(item)

            
            formatted_item = {
                    assigned_items_loan_nos_model.emp_id: item['loanNumber'],          # Rename loanNumber to emp_id
                    assigned_items_loan_nos_model.employee_name: item['assignedName'], # Rename assignedName to employee_name
                    assigned_items_loan_nos_model.date: item['date'],                  # Keep date as it is
                    assigned_items_loan_nos_model.loan_number: item['loanNumber'],     # Keep loanNumber as it is
                    assigned_items_loan_nos_model.item_name: item['itemName'],         # Keep itemName as it is
                    assigned_items_loan_nos_model.part_number: item['partNumber'],     # Keep partNumber as it is
                    assigned_items_loan_nos_model.quantity: item['quantity'],           # Keep quantity as it is
                    assigned_items_loan_nos_model.emp_id : get_emp_id(item['assignedName'])
            }
            # Creating entry in the assigned inventory table of new assigned item
            create_document(assigned_items_loan_nos_model.table, formatted_item) 

            # PART 3 - Increase total value of items assigned

            # TODO Increase the number in the total quantity so that it can be accessed in the mobile application

            temp_emp_id = get_emp_id(item['assignedName'])
            if item_already_assigned(temp_emp_id, item['partNumber']):
                param = {

                     assigned_items_model.emp_id : temp_emp_id,
                    assigned_items_model.part_number : item['partNumber']
                }
                doc = read_documents(assigned_items_model.table, param)
                id = get_document_id(assigned_items_model.table, param)
                    
                # Increasing the quantity of the assigned item 
                quant = int(doc[0]['quantity']) + int(item['quantity'])
                    
                # Updating the items table with increased quantity
                data = {assigned_items_model.quantity: quant}
                update_document(assigned_items_model.table, id, data)

                print("Increase the quantity of existing item")
            else:
                # Creating entry in the assigned inventory table of new assigned item

                assigned_item = {
                    assigned_items_model.emp_id : temp_emp_id,
                    assigned_items_model.item_name : item['itemName'],
                    assigned_items_model.part_number : item['partNumber'],
                    assigned_items_model.quantity : item['quantity']
                }
                create_document(assigned_items_model.table, assigned_item) 

        return jsonify({'message':'Assigning data succesful!'})

    except Exception as e:
        print("An error occurred:", e)
        return jsonify({'message':'Error assigning data!'})
        # Handle the error here or re-raise it if needed
        # raise e




def item_exists(part_number):

    params = {
        item_model.part_number : part_number,
        item_model.location : session['location']
    } 

    if read_documents(item_model.table,params):
        return True
    
    return False

def item_already_assigned(emp_id, part_number):
    params = {
        assigned_items_model.emp_id : emp_id,
        assigned_items_model.part_number : part_number,
    } 

    if read_documents(assigned_items_model.table, params):
        return True
    
    return False