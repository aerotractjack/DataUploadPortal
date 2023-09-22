import requests

def get_filetypes():
    url = "http://127.0.0.1:5055/api/get_filetypes"
    req = requests.post(url)
    return req.json()

def get_clients():
    try:
        url = "http://127.0.0.1:5055/api/get_client_names_ids"
        req = requests.post(url)
        return req.json()
    except:
        return []

def get_projects(client_id):
    try:
        url = "http://127.0.0.1:5055/api/get_project_names_ids"
        req = requests.post(url, json={"id": client_id})
        return req.json()
    except:
        return []

def get_stands(project_id):
    try:
        url = "http://127.0.0.1:5055/api/get_stand_names_ids"
        req = requests.post(url, json={"id": project_id})
        return req.json()
    except:
        return []

if __name__ == "__main__":
    print(get_filetypes())
    print(get_clients())
    print(get_projects(10007))
    print(get_stands(101036))