from datetime import datetime
import requests

def log_crm_heartbeat():
    log_file= "/tmp/crm_heartbeat_log.txt"
    timestamp= datetime.now().strftime('%d-%m-%Y-%H:%M:%S')

# not amust
    graphql_url= "http://localhost:8000/graphql"
    query= {"query": "{hello}"}

    try:
        response= requests.post(graphql_url, json=query, timeout=5)
        if response.status_code == 200:
            msg=f"{timestamp} CRM is okay"
        else:
            msg= f"{timestamp} CRM heartbeat - Graphql responded with {response.status_code}"
    
    except Exception as e:
        msg= f"{timestamp} CRM heartbeat - Graphql check failed: {e}"

    with open(log_file, "a") as f:
        f.write(msg + "\n")