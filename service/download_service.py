import os
from flask import session
import pandas as pd

from firebase import read_documents, read_documents_startswith

from model import employee_model, item_model

def generate_download_file(collection_name):
      
    # different case for items, rest all using emp id starting
    
    prefix = None
    data = None 

    if session['location'] == 'gurgaon':
        prefix = 'ggn'
    elif session['location'] == 'faridabad':
        prefix = 'far'
    else :
        return
    
    if collection_name == "items" or collection_name == 'assets':
        params = {
            item_model.location : session['location']
        }
        data = read_documents(collection_name, params)
    else :
        data = read_documents_startswith(collection_name, employee_model.emp_id,prefix)

    print(data)

    df = pd.DataFrame(data)
    excel_filename = collection_name + ".xlsx"

    # Get the root directory of your project
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # Go one directory up
    parent_dir = os.path.dirname(root_dir)

    # Join the parent directory with your filename
    full_path = os.path.join(parent_dir, excel_filename)

    df.to_excel(full_path, index=False)
    return full_path

