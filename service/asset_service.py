from flask import jsonify, session
from firebase import create_document, read_documents, update_document, get_document_id
from model import asset_model, assigned_asset_model
from utils import get_emp_id

def add_asset(data):
    print('asset added')
    for key, value in data.items():
        data[key] = value.strip()

    if asset_exists(data['serial_number']):
        return jsonify({'status': 'exists'})
    print('moving forward ')
    # If asset does not exist, add it to the collection
    asset_data = {
        asset_model.asset_name: data['asset_name'],
        asset_model.asset_type: data['asset_type'],
        asset_model.quantity: int(data['quantity']),
        asset_model.serial_number: data['serial_number'],
        asset_model.location: session['location']
    }

    # Save the data to Firebase
    create_document(asset_model.table, asset_data)
    return jsonify({'status': 'Successfully Added Asset!'})

#update asset 

def update_asset(asset_data):

    # Getting the increment value
    update_quantity=int(asset_data['quantity'])

    params = {
    asset_model.serial_number : asset_data['serial_number'],
    asset_model.location : session['location']
    }

    # Getting current quantity
    document_id = get_document_id(asset_model.table, params)
   
    temp=read_documents(asset_model.table, params)


    # Increasing the quantity
    update_quantity+=int(temp[0]['quantity'])

    # Updating the new quantity in firebase
    data = {asset_model.quantity: update_quantity} 
    return update_document(asset_model.table, document_id, data)

# Assign Asset 
def assign_asset(data):
    try:
        for asset in data:
            # PART 1 - Decrease Total Inventory
            asset_name = asset['asset_name']
            asset_quantity = asset['quantity']
            serial_number = asset['serial_number']
            employee_name = ['employee_name']
            asset_type =['asset_type']
            param = {
                asset_model.serial_number : serial_number,
                asset_model.location : session['location']
            }
            doc = read_documents(asset_model.table, param)
            id = get_document_id(asset_model.table, param)

            # Decreasing the quantity from total inventory 
            quant = int(doc[0]['quantity']) - int(asset_quantity)

            # Updating the items table with decreased quantity
            data = {'quantity': quant}
            update_document(asset_model.table, id, data)

            print(asset)
            # PART 2 - Increase total value of items assigned

            # TODO Increase the number in the total quantity so that it can be accessed in the mobile application

            temp_emp_id = get_emp_id(asset['assigned_name'])
            if asset_already_assigned(temp_emp_id, asset['serial_number']):
                param = {

                    assigned_asset_model.emp_id : temp_emp_id,
                    assigned_asset_model.serial_number : asset['serial_number']
                }
                doc = read_documents(assigned_asset_model.table, param)
                id = get_document_id(assigned_asset_model.table, param)
                    
                # Increasing the quantity of the assigned item 
                quant = int(doc[0]['quantity']) + int(asset['quantity'])
                    
                # Updating the items table with increased quantity
                data = {assigned_asset_model.quantity: quant}
                update_document(assigned_asset_model.table, id, data)

                print("Increase the quantity of existing item")
            else:
            # Creating entry in the assigned inventory table of new assigned item
                assigned_asset = {
                assigned_asset_model.emp_id : temp_emp_id,
                assigned_asset_model.asset_name : asset['asset_name'],
                assigned_asset_model.serial_number : asset['serial_number'],
                assigned_asset_model.quantity : asset['quantity'],
                assigned_asset_model.employee_name: asset['assigned_name'],
                assigned_asset_model.asset_type: asset['asset_type'] 
                }
                create_document(assigned_asset_model.table, assigned_asset)

        return jsonify({'message':'Assigning data succesful!'})

    except Exception as e:
        print("An error occurred:", e)
        return jsonify({'message':'Error assigning data!'})
        # Handle the error here or re-raise it if needed
        # raise e


def asset_exists(serial_number):

    params = {
        asset_model.serial_number : serial_number,
        asset_model.location : session['location']
    } 

    if read_documents(asset_model.table,params):
        return True
    
    return False

def asset_already_assigned(emp_id, serial_number):
    params = {
        assigned_asset_model.emp_id : emp_id,
        assigned_asset_model.serial_number : serial_number,
    } 

    if read_documents(assigned_asset_model.table, params):
        return True
    
    return False