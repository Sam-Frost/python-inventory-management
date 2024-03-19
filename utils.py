import random
from firebase import read_documents
from model import employee_model
import consts
from datetime import datetime


def random_error_image():
    error_number = random.randint(1, 4)
    return f"error{error_number}.jpeg"

def nav_init(nav, request_path):
    # Iterate over the navbar links
    for link in nav:
        if link['href'] == request_path:
            link['status'] = 'active'
        else :
            link['status'] = 'inactive'
    return nav

def get_emp_id(name):
    params = {
            employee_model.employee_name : name
    }
    return read_documents(employee_model.table, params)[0]['emp_id']

def parse_items(items_str):
    items_dict = {}
    items_list = items_str.split('\n')
    for item in items_list:
        parts = item.split(' x ')
        if len(parts) == 2:
            item_name, quantity = parts
            items_dict[item_name.strip()] = int(quantity)
    return items_dict


def location_from_emp_id(emp_id):
    if emp_id.startswith(consts.GURGAON_PREFIX) :
        return 'gurgaon'
    elif emp_id.startswith(consts.FARIDABAD_PREFIX) :
        return 'faridabad'
    else :
        return ValueError 
    

def sort_objects_by_date(objects, key='date', reverse=True):
    # Define a function to extract the date from each object
    def extract_date(obj):
        # Assuming the date is stored as a string attribute named 'date'
        date_str = obj.get(key)
        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj

    # Sort the objects using the extract_date function as key
    sorted_objects = sorted(objects, key=extract_date, reverse=reverse)
    return sorted_objects
