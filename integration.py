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

if __name__ == "__main__":
    s = get_stands(101037)
    for x in s:
        print(x["STAND_ID"])