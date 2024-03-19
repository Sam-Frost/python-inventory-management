import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


current_dir = os.path.dirname(__file__)
firebase_json_path = os.path.join(current_dir, "firebase.json")

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_json_path)
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()


def read_documents(collection_name, parameters=None):
    print(f"Reading documents for {collection_name}!")
    try:
        # Create a reference to the collection
        collection_ref = db.collection(collection_name)

        if parameters:
            # Query documents based on parameters
            query = collection_ref
            for key, value in parameters.items():
                query = query.where(field_path=key, op_string='==', value=value)

            # Get documents
            documents = query.stream()
        else:
            # List all documents in the collection
            documents = collection_ref.stream()

        # Extract data from documents
        results = []
        for doc in documents:
            results.append(doc.to_dict())

        return results

    except Exception as e:
        print("An error occurred:", e)
        return None
    
def create_document(collection_name, data):
    print(f"Creating document in {collection_name}. Data :\n{data}\n")
    try:
        # Create a reference to the collection
        collection_ref = db.collection(collection_name)

       # Add the document to the collection
        result = collection_ref.add(data)

        # Extract document reference object from the result tuple
        document_ref = result[1]

        print("Document created with ID:", document_ref.id)
        return document_ref.id
        # return result

    except Exception as e:
        print("An error occurred:", e)
        return None

def get_document_by_id(collection_name, document_id):
    print(f"Getting document from {collection_name} with  {document_id}")
    try:
        # Create a reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        # Get the document
        doc = doc_ref.get()

        # Check if the document exists
        if doc.exists:
            return doc.to_dict()
        else:
            print(f"Document with ID {document_id} does not exist.")
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None
    

def update_document(collection_name, document_id, update_data):
    print(f"Updating document in {collection_name}. ID: {document_id} \n{update_data}\n")
    try:
        # Create a reference to the document
        doc_ref = db.collection(collection_name).document(document_id)

        # Update the document
        doc_ref.update(update_data)

        print(f"Document with ID {document_id} updated successfully.")
        return True

    except Exception as e:
        print("An error occurred:", e)
        return False
    
def read_documents_startswith(collection_name, field_name, prefix):
    print(f"Reading documents in {collection_name}  who's '{field_name}' start's with '{prefix}' ")
    try:

        # Create a reference to the collection
        collection_ref = db.collection(collection_name)

        # Query documents where the field value starts with the prefix
        query = collection_ref.where(field_name, ">=", prefix).where(field_name, "<", prefix + u"\uf8ff")
        documents = query.stream()

        # Extract data from documents
        results = []
        for doc in documents:
            results.append(doc.to_dict())

        return results

    except Exception as e:
        print("An error occurred:", e)
        return None
    
def get_document_id(collection_name, query_params):
    print("Get document ID function called for ${collection_name}. Data : \n{query_params}\n")
    try:
        collection_ref = db.collection(collection_name)
        for field, value in query_params.items():
            collection_ref = collection_ref.where(field, '==', value)
        
        query_ref = collection_ref.stream()
        
        for doc in query_ref:
            return doc.id
        
        return None
    except Exception as e:
        print("An error occurred:", e)
        return "Error in Firebase operation"