import requests
import pandas as pd 

url = "http://127.0.0.1:5055"

def healthcheck():
    return requests.get(url+"/health").json()

def client_ids():
    endp = url + "/api/get_options"
    req = requests.post(endp, json={
        "table_name": "clients",
        "cols": ["CLIENT_ID"]
    })
    return [str(c) for c in req.json()["CLIENT_ID"]]

def project_ids_by_client():
    out = {}
    cids = client_ids()
    for cid in cids:
        pid_req = requests.post(url+"/api/query",json={
            "json_query": {
                "table": "projects",
                "cols": ["PROJECT_ID"],
                "queries": [{
                    "qtype": "EQUAL",
                    "search": "CLIENT_ID",
                    "match": cid
                }]
            }
        })
        if pid_req.status_code != 200:
            continue
        pids = [str(p["PROJECT_ID"]) for p in pid_req.json()]
        out[cid] = pids
    return out

def stand_pids_by_project():
    out = {}
    endp = url + "/api/get_options"
    req = requests.post(endp, json={
        "table_name": "projects",
        "cols": ["PROJECT_ID"]
    })
    pids = req.json()["PROJECT_ID"]
    for pid in pids:
        spid_req = requests.post(url+"/api/query",json={
            "json_query": {
                "table": "stand_project_mapping",
                "cols": ["STAND_PERSISTENT_ID"],
                "queries": [{
                    "qtype": "EQUAL",
                    "search": "PROJECT_ID",
                    "match": pid
                }]
            }
        })
        if spid_req.status_code != 200:
            continue
        _spids = [sp["STAND_PERSISTENT_ID"] for sp in spid_req.json()]
        spids = []
        for sp in _spids:
            if sp is None:
                continue
            try:
                spids.append(str(int(sp)))
            except:
                pass
        out[pid] = spids
    return out

def get_dropdown_data():
    return [
        client_ids(),
        project_ids_by_client(),
        stand_pids_by_project()
    ]


if __name__ == "__main__":
    import json
    print(json.dumps(get_dropdown_data(), indent=2))