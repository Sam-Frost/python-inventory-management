
# Inventory Management System
  
This Flask-based web application serves as an inventory management system, while also functioning as the backend for a Flutter mobile application—a pivotal component of the overall inventory management system. 

**General User Flow :** Users have the capability to manage employees, items, and assets within the system. Employees are assigned specific items to utilize in their daily tasks. Using a mobile application, employees can generate requests to utilize items allocated to them. Once these requests are approved via the web-based admin portal, employees can proceed to generate bills for the items they have utilized.

## Technologies Used

-   HTML5 (HTML,  CSS, JS)
-   Python ( Flask, Pandas)
-   Firebase

## Folder Structure

### Folders
- <b>Model : </b> This folder contains all the **collection** and their corresponding **field names**.
- <b>Service : </b> This folder contains all the collection and their corresponding field names.
- <b>Template : </b> This folder contains all the **html** files.
- <b>Static : </b> This folder contains all static resources like **images, css, javascript files**

### Files
- **app.py** : This is the main web server code.
- **api.py**: This files contains all the  **Rest API Endpoints** for the flutter mobile app.

## Installation

1.  Clone the repository:
	
	`git clone https://github.com/your-username/your-project.git` 
	
2.  Install dependencies:

    `pip install -r requirements.txt` 
    
3.  Set up Firebase:
    
    - Create a Firebase project.
    - Set up cloud firestore
    - Create a collection `'admin'`
    - Add a document as follows :
    - <img width="261" alt="Screenshot 2024-04-04 at 9 12 42 PM" src="https://github.com/Sam-Frost/python-inventory-management/assets/40019398/25027a41-2d9f-4976-bcce-e380b501580e">
    - Location can either be `"gurgaon" or "faridabad"`
    - Create a collection `'variables'`
    - Add 2 document as follows(set the value as 0):
    - <img width="226" alt="Screenshot 2024-04-04 at 9 13 10 PM" src="https://github.com/Sam-Frost/python-inventory-management/assets/40019398/b37cccf3-793b-4661-9fb9-dc3aca666978">
    - <img width="238" alt="Screenshot 2024-04-04 at 9 13 30 PM" src="https://github.com/Sam-Frost/python-inventory-management/assets/40019398/52de1411-f301-419d-a3c6-65593ae7f4db">
    - Add your Firebase Service Account Key to `./firebase.json`.
    
4. Add a file '`./static/config.js'`

5. `"config.js"` content : `window.my_website_url = "http://127.0.0.1:5000";`

## Usage

How to run the project:

1.  Start the Flask server:
    
    `python app.py` 
    
2.  Open the web app in your browser:
   
    `http://localhost:5000` 
    
3. Login using the credentials created while setting up:
	ID : 
	Password : 
 
    

