# wget -q https://git.io/vFb1J -O /tmp/setupmongodb.sh && source /tmp/setupmongodb.sh
import pymongo
import os

MONGODB_URI = os.getenv("MONGO_URI")
DBS_NAME = "diplomacydb"
COLLECTION_NAME = "diplomacydb"

def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s") % e
        
def show_menu():
    print("")
    print("1. Add a record")
    print("2. Find a record by name")
    print("3. Edit a record")
    print("4. Delete a record")
    print("5. Exit")
    
    option = input("Enter option: ")
    return option
    
def get_record():
    print("")
    first = input("Enter first name: ")
    last = input("Enter last name: ")
    try:
        doc = coll.find_one({'first': first.lower(), 'last': last.lower()})
    except:
        print("error")
    if not doc:
        print("")
        print("no results found")
    return doc
    
def add_record():
    print("")
    first = input("Enter first name: ")
    last = input("Enter last name: ")
    new_doc = {
        'first': first.lower(),
        'last': last.lower(),
    }
    try:
        coll.insert(new_doc)
        print("")
        print("document inserted")
    except:
        print("error")
        
def find_record():
    doc = get_record()
    if doc:
        print("")
        for k, v in doc.items():
            if k != "_id":
                print(k.capitalize() + ": " + v.capitalize())
                
def edit_record():
    doc = get_record()
    if doc:
        update_doc={}
        for k, v in doc.items():
            if  k != "_id":
                update_doc[k] = input(k.capitalize() + " [" + v + "] : ").lower()
                
                if update_doc[k] == "":
                    update_doc[k] = v
        try:
            coll.update_one(doc, {'$set': update_doc})
            print("")
            print("Document updated")
        except:
            print("error")
            
def delete_record():
    doc = get_record()
    if doc:
        print("")
        for k, v in doc.items():
            if k != "_id":
                print(k.capitalize() + ": " + v.capitalize())
        print("")
        confirmation = input("Is this the document you want to delete?\nY/N").lower()
        if confirmation == "y":
            try:
                coll.remove(doc)
                print("Document deleted!")
            except: 
                print("error")
        else: 
            print("document not deleted")
                
    
def main_loop():
    while True:
        option = show_menu()
        if option == "1":
            add_record()
        elif option == "2":
            find_record()
        elif option == "3":
            edit_record()
        elif option == "4":
            delete_record()
        elif option == "5":
            conn.close()
            break
        else:
            print("Invalid option")
        print("")
        
conn = mongo_connect(MONGODB_URI)
coll = conn[DBS_NAME][COLLECTION_NAME]

main_loop()