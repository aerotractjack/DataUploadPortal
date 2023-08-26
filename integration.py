import pandas as pd
import yaml
import requests

def get_dropdown_data():
    # use the DB API to get our clients, projects, and sites
    url = "http://192.168.1.35:5055/api/project_and_stand_ids"
    req = requests.post(url)
    data = pd.DataFrame(req.json())
    cids = data["CLIENT_ID"].sort_values().unique().tolist()
    pid_map = {}
    for cid in cids:
        pids = data[data["CLIENT_ID"] == cid]["PROJECT_ID"]
        pid_map[str(cid)] = [str(_) for _ in pids.sort_values().unique().tolist()]
    sid_map = {}
    for pid in data["PROJECT_ID"].sort_values().unique().tolist():
        sids = data[data["PROJECT_ID"] == pid][["STAND_ID", "STAND_PERSISTENT_ID"]]
        sids = sids.to_dict("records")
        sid_map[str(pid)] = [str(_) for _ in sids]
    return [[str(_) for _ in cids], pid_map, sid_map]

def get_filetypes():
    url = "http://192.168.1.35:5055/api/get_filetypes"
    req = requests.post(url)
    return req.json()