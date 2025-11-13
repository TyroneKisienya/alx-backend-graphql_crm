from datetime import datetime
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    log_file= "/tmp/crm_heartbeat_log.txt"
    timestamp= datetime.now().strftime('%d-%m-%Y-%H:%M:%S')

    transport= RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )

# not amust
    client = Client(transport=transport,fetch_schema_from_transport=False)
    query= gql(
        """
            query{
            hello
            }
        """
    )

    try:
        response= client.execute(query)
        hello_message= response.get("hello", "No response")
        msg= f"{timestamp} CRM is alive Saying {hello_message}"
    except Exception as e:
        msg= f"{timestamp} CRM heartbeat - Graphql check failed: {e}"

    with open(log_file, "a") as f:
        f.write(msg + "\n")