import requests
from config import api_url, storage_api_url

def get_filetypes():
    url = f"{api_url}/api/get_filetypes"
    req = requests.post(url)
    return req.json()

def get_clients():
    try:
        url = f"{api_url}/api/get_client_names_ids"
        req = requests.post(url)
        return req.json()
    except:
        return []

def get_projects(client_id):
    try:
        url = f"{api_url}/api/get_project_names_ids"
        req = requests.post(url, json={"id": client_id})
        return req.json()
    except:
        return []

def get_stands(project_id):
    try:
        url = f"{api_url}/api/get_stand_names_ids"
        req = requests.post(url, json={"id": project_id})
        stands = req.json()
        return sorted(stands, key=lambda x: x["STAND_ID"])
    except:
        return []
    
def get_stand_pid_from_ids(client_id, project_id, stand_id):
    try:
        url = f"{api_url}/api/stand_pid_from_ids"
        req = requests.post(url, json={"client_id": client_id, "project_id": project_id, "stand_id": stand_id})
        return req.json()[0]["STAND_PERSISTENT_ID"]
    except:
        return  []
    
def post_update(update):
    url = f"{storage_api_url}/update" 
    body = {"entry": update}
    req = requests.post(url, json=body)
    if not req.status_code == 200:
        raise ValueError("STORAGE ERROR: " + req.text)
    return True

def client_id_from_project_id(project_id):
    try:
        url = f"{api_url}/api/get_client_id_from_project"
        req = requests.post(url, json={"project_id": project_id})
        return req.json()[0]["CLIENT_ID"]
    except:
        return  []