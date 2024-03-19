
from functools import wraps
from flask import Flask, jsonify, redirect, render_template, request, send_file, session, url_for
from firebase import get_document_id, read_documents, read_documents_startswith, update_document

import navbars
from service import download_service

from utils import nav_init, random_error_image, sort_objects_by_date

from service import login_service, employee_service, item_service, good_service, defective_inventory_service, approval_service, asset_service
from model import approval_model, assigned_items_model, employee_model, item_model, assigned_items_loan_nos_model, good_return_model, defective_items_model, asset_model, assigned_asset_model


import pandas as pd
import consts

from api import api

from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.secret_key = "b_5#y2LF4Q8z\n\xec]/"
app.config['JWT_SECRET_KEY'] = 'b_5#y2LF4Q8z\n\xec]/'  
 
jwt = JWTManager(app)

# Simulating user login status
user_logged_in = False

# Custom decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global user_logged_in
        if not user_logged_in:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# API endpoints router
app.register_blueprint(api,url_prefix='/api/v1')


# #########  LOGIN/LOGOUT/DASHBOARD  ROUTES ################
@app.route('/login', methods=['GET','POST'])
def login():
    print("Login route called!")

    if request.method == 'GET':
        return render_template('login_dashboard/signin.html')
    
    if request.method == 'POST':

        session.clear()

        email = request.form.get('email')
        password = request.form.get('password')

        result = login_service.login(email, password)

        print(result)
        if result:
            
            global user_logged_in
            session['user_logged_in'] = True
            session['username'] = result[0]['username']
            session['location'] = result[0]['location']
            session['name'] = result[0]['name']
            user_logged_in=True

            print("-"*5 + "LOGING IN" + "-"*5)
            print(session['username'] + "   " + session['location'] + "   " +  session['name'] + "   ") 
            print("-"*5 + "LOGING IN" + "-"*5)

        else:
            return render_template("error.html", msg="User not found!", error_image=random_error_image())

        return redirect("/")
    
@app.context_processor
def inject_variables():
    name = session.get('name', '')  # Get the 'name' session variable, or default to an empty string if it's not set
    return {'name': name}

@app.route('/logout')
def logout():
    print("Logout route called!")
    session.clear()
    return redirect(url_for('login'))



# TODO TO BE TESTED WHEN TEHRE IS DATA
@app.route('/')
@login_required
def dashboard():
    print("Dashboard route called!")
    prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
    inventory=read_documents_startswith(assigned_items_loan_nos_model.table, employee_model.emp_id, prefix)
    # approval = read_all_documents(approval_model.table)

    # if (not approval) or (not inventory):
        # return render_template("error.html", msg="Error in firebase operation!", error_image=random_error_image())

    # return render_template('login_dashboard/dashboard.html',inventory=inventory, approval=approval)

    return render_template('login_dashboard/dashboard.html',inventory=inventory, approval=[])
# ------------------------------------

# #########  EMPLOYEE  ROUTES ################
@app.route('/employee_registration', methods=['POST', 'GET'])
@login_required
def employee_registration():
    print("Employee Registration route called!")

    if request.method == 'POST':
        data = request.json
        return employee_service.register_employee(data)
    
    else :
        nav = nav_init(navbars.employee_navbar, request.path)
        return render_template('employee/employee_registration.html', navbar_values=nav)
    
@app.route('/show_employee')
@login_required
def show_employee():
    print("Show  Employee route called!")

    prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
    data=read_documents_startswith(employee_model.table, employee_model.emp_id, prefix)

    nav = nav_init(navbars.employee_navbar, request.path)
    return render_template('employee/employee_list.html', data=data, navbar_values=nav)
# ------------------------------------

# #########  INVENTORY  ROUTES ################
@app.route('/show_item')
@login_required
def show_item():
    print("Show Item route called!")
    params = {
        item_model.location : session['location']
    }
    inventory = read_documents(item_model.table, params)

    # if not inventory :
    #     return render_template("error.html", msg="Error in firebase operation!", error_image=random_error_image())
    
    nav = nav_init(navbars.inventory_navbar, request.path)
    return render_template('item/show_item.html',data=inventory, navbar_values = nav )

@app.route('/add_item', methods=['POST', 'GET'])
@login_required
def add_inventory():
    print("Add Item route called!")
    if request.method == 'POST':

        data = request.json 
        return item_service.add_item(data)
    
    nav = nav_init(navbars.inventory_navbar, request.path)
    return render_template('item/add_item.html', navbar_values = nav)

@app.route('/update_item', methods = ['GET', 'POST'])
@login_required
def update_item():
    print("Update Item route called!")
    nav = nav_init(navbars.inventory_navbar, request.path)

    if request.method == 'GET':
        params = {
            item_model.location :  session['location']
        }
        data=read_documents(item_model.table, params)
        return render_template('item/update_item.html', data=data, navbar_values = nav )
    else:
        item_data = request.json

        result = item_service.update_item(item_data)

        if not result:
            return render_template("error.html", msg="Error in firebase operation!", error_image=random_error_image())
        
        return render_template('item/update_item.html', navbar_values = nav)


@app.route('/assign_item', methods = ["GET", 'POST'])
@login_required
def assign_item():
    print("Assign Inventory route called!")
    if request.method == 'GET':
        param = {
            item_model.location : session['location']
        }
        items=read_documents(item_model.table, param)

        prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
        employees=read_documents_startswith(employee_model.table, employee_model.emp_id, prefix)

        full_names = [employee[employee_model.employee_name] for employee in employees]

        if (not items) or (not employees):
            return render_template("error.html", msg="Error in firebase operation!", error_image=random_error_image())
        
       
        nav = nav_init(navbars.inventory_navbar, request.path)
        return render_template('item/assign_item.html', data=items, full_names=full_names, navbar_values = nav)    

    else: 
        data = request.json
        return item_service.assign_item(data)

# ------------------------------------
    

# #########  GOODS  ROUTES ################
@app.route('/good_assigned')
@login_required
def good_assigned():
    print("Good Assigned route called!")
    
    prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
    data=read_documents_startswith(assigned_items_loan_nos_model.table, employee_model.emp_id, prefix)

    nav = nav_init(navbars.good_navbar, request.path)
    return render_template('good/good_assigned.html',data=data, navbar_values=nav)

@app.route('/good_return', methods=['GET', 'POST'])
@login_required
def good_return():
    print("Good Return route called!")
    if request.method == 'POST':
        data = request.json
        return good_service.add_good_return(data)
    
    else :

        param = {
            item_model.location : session['location']
        }
        items = read_documents(item_model.table, param)
        item_names = [item["item_name"] for item in items]

        prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
        employees=read_documents_startswith(employee_model.table, employee_model.emp_id, prefix)
        employee_names = [employee["employee_name"] for employee in employees]

        nav = nav_init(navbars.good_navbar, request.path)
        return render_template('good/good_return.html', item_names=item_names, employee_names=employee_names, navbar_values=nav)

@app.route('/good_return_list')
@login_required
def good_return_list():
    print("Good Return List route called!")

    prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
    data=read_documents_startswith(good_return_model.table, employee_model.emp_id, prefix)


    nav = nav_init(navbars.good_navbar, request.path)
    return render_template('good/good_return_list.html',data=data, navbar_values=nav)
# ------------------------------------
    

# #########  DEFECTIVE/WRITE-OFF/SEND-TO-VENDORS   ROUTES ################
@app.route('/defective_list')
@login_required
def defective_list():
    print("Defective List route called!")

    prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
    data=read_documents_startswith(defective_items_model.table, employee_model.emp_id, prefix)

    nav = nav_init(navbars.defective_inventory_navbar, request.path)
    return render_template('defective/defective_list.html', data=data, navbar_values=nav)


@app.route('/defective_in', methods=['POST', 'GET'])
@login_required
def defective_in():
    print("Defective In route called!")
    if request.method == 'POST':

        data = request.json
        return defective_inventory_service.add_defective_inventory(data)

    else :
        param = {
            item_model.location : session['location']
        }
        items = read_documents(item_model.table, param)
        item_names = [item["item_name"] for item in items]

        prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
        employees = read_documents_startswith(employee_model.table, employee_model.emp_id, prefix)
        employee_names = [employee["employee_name"] for employee in employees]
    
        nav = nav_init(navbars.defective_inventory_navbar, request.path)
        return render_template('defective/defective_in.html', employee_names=employee_names, item_names = item_names, navbar_values=nav)

@app.route('/write_off', methods=['POST','GET'])
@login_required
def write_off():
    print("Write Off route called!")
    if request.method == 'POST':
        data=request.json
        return defective_inventory_service.write_off(data)
    if request.method=='GET':
        

        prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
        data=read_documents_startswith(defective_items_model.table, employee_model.emp_id, prefix)

        filterd_data = []

        for doc in data:
            if  doc['status'] == "write_off" :
                filterd_data.append(doc)


        # Customizing Navbar
        nav = nav_init(navbars.defective_inventory_navbar, request.path)
        return render_template('write_off.html',data=filterd_data, navbar_values=nav)

@app.route('/send_to_vendor', methods=['POST','GET'])
@login_required
def send_to_vendor():
    print("Send To Vendor route called!")
    if request.method == 'POST':
        data=request.json
        return defective_inventory_service.send_to_vendor(data)
    if request.method=='GET':

        prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
        data=read_documents_startswith(defective_items_model.table, employee_model.emp_id, prefix)
        filterd_data = []

        for doc in data:
            if  doc['status'] == "send_to_vendor" :
                filterd_data.append(doc)

        # Customizing Navbar
        nav = nav_init(navbars.defective_inventory_navbar, request.path)
        return render_template('vendor_data.html',data=filterd_data, navbar_values=nav)
# ------------------------------------
    


# #########  APPROVAL  ROUTE ################
@app.route('/approval_inventory', methods = ['GET', 'POST'])
@login_required
def approval_inventory():
    print("Approval Inventory route called!")
    if request.method == 'GET':
        prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
        data=read_documents_startswith(approval_model.table, employee_model.emp_id, prefix)
        print(data)
        data = sort_objects_by_date(data)
        return render_template('approval/approval_inventory.html', data=data)
    else : 
        response_data = request.json
        return approval_service.approval_inventory(response_data)


# TODO  : DON"T KNOW WHAT THIS ROUT IS FOR
@app.route('/approved_inventory')
def approved_inventory():
    print("Approved Inventory route called!")

    prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
    data=read_documents_startswith(approval_model.table, employee_model.emp_id, prefix)

    return render_template('approval/approved_inventory.html',data=data)
# ------------------------------------




# #########  DOWNLOAD  ROUTE ################
@app.route('/download',methods=['POST'])
@login_required
def download_collection():
    print("Download route called!")
    if request.method=='POST':

        collection_name = request.form.get('collection_name')
        download_file = download_service.generate_download_file(collection_name)
        return send_file(download_file, as_attachment=True)
# ------------------------------------

# ############ ASSET ROUTE ############
@app.route('/asset_add', methods= ['POST', 'GET'])
@login_required
def asset_add():
    print("Add asset route is called ")
    if request.method == 'POST':
        data = request.json 
        return asset_service.add_asset(data)

    nav = nav_init(navbars.asset_navbar, request.path)
    return render_template('asset/asset_add.html', navbar_values = nav)
        

@app.route('/asset_update', methods = ['GET', 'POST'])
@login_required
def asset_update():
    print("Update asset route called!")
    nav = nav_init(navbars.asset_navbar, request.path)

    if request.method == 'GET':
        params = {
            asset_model.location :  session['location']
        }
        data=read_documents(asset_model.table, params)
        return render_template('asset/asset_update.html', data=data, navbar_values = nav )
    else:
        item_data = request.json

        result = asset_service.update_asset(item_data)

        if not result:
            return render_template("error.html", msg="Error in firebase operation!", error_image=random_error_image())
        
        return render_template('asset/asset_update.html', navbar_values = nav)

@app.route('/asset_show')
@login_required
def asset_show():
    print("Show Asset route called!")
    params = {
        asset_model.location : session['location']
    }
    assets = read_documents(asset_model.table, params)

    # if not assets :
    #     return render_template("error.html", msg="Error in firebase operation!", error_image=random_error_image())
    
    nav = nav_init(navbars.asset_navbar, request.path)
    return render_template('asset/asset_show.html',data=assets, navbar_values = nav )


@app.route('/asset_assign', methods = ["GET", 'POST'])
@login_required
def asset_assign():
    print("Assign Asset route called!")
    if request.method == 'GET':
        param = {
            asset_model.location : session['location']
        }
        assets=read_documents(asset_model.table, param)

        prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
        employees=read_documents_startswith(employee_model.table, employee_model.emp_id, prefix)

        full_names = [employee[employee_model.employee_name] for employee in employees]

        if (not assets) or (not employees):
            return render_template("error.html", msg="Error in firebase operation!", error_image=random_error_image())
        
       
        nav = nav_init(navbars.asset_navbar, request.path)
        return render_template('asset/asset_assign.html', assets=assets, names=full_names, navbar_values = nav)    

    else: 
        data = request.json
        return asset_service.assign_asset(data)

@app.route('/asset_assigned')
@login_required
def asset_assigned():
    print("Asset Assigned route called!")
    
    prefix = consts.GURGAON_PREFIX if session['location'] ==  'gurgaon' else consts.FARIDABAD_PREFIX
    data=read_documents_startswith(assigned_asset_model.table, employee_model.emp_id, prefix)

    nav = nav_init(navbars.asset_navbar, request.path)
    return render_template('asset/asset_assigned.html',data=data, navbar_values=nav)        

if __name__== "__main__" :
    app.run(debug=True)
