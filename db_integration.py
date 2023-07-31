import requests
import pandas as pd 

url = "http://127.0.0.1:5055/api/project_and_stand_ids"

def get_dropdown_data():
    req = requests.post(url)
    data = pd.DataFrame(req.json())
    cids = data["CLIENT_ID"].sort_values().unique().tolist()
    pid_map = {}
    for cid in cids:
        pids = data[data["CLIENT_ID"] == cid]["PROJECT_ID"]
        pid_map[cid] = pids.sort_values().unique().tolist()
    sid_map = {}
    for pid in data["PROJECT_ID"].sort_values().unique().tolist():
        sids = data[data["PROJECT_ID"] == pid][["STAND_ID", "STAND_PERSISTENT_ID"]]
        sids = sids.to_dict("records")
        sid_map[pid] = sids
    return [cids, pid_map, sid_map]

if __name__ == "__main__":
    import json
    data = get_dropdown_data()
    print(json.dumps(data, indent=4))