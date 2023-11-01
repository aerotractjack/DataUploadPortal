import requests
from config import api_url

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
        return 
    
if __name__ == "__main__":
    # print(get_filetypes())
    # print(get_clients())
    # print(get_projects(10007))
    # print(get_stands(101036))
    print(get_stand_pid_from_ids(10009, 101005, 205))
