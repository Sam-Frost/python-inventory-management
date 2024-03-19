from firebase import read_documents
from model import admin_model

def login(username, password):
    print("Login Service! login function called!")

    parameters = {
        'username' : username,
        'password' : password
    }

    # TODO BYPASED FOR TESTING, ADD required attribute in signin html
    # parameters = {
    #     'username' : "admingurgaon",
    #     'password' : "securepassword"
    # }

    # parameters = {
    #     'username' : "faridabaduser",
    #     'password' : "faridabadpassword"
    # }

    return read_documents(admin_model.table, parameters)


