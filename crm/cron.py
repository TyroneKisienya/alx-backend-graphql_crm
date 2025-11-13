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

def update_low_stock():
    log_file= "/tmp/low_stock_updates_log.txt"
    timestamp= datetime.now().strftime("%d-%m-%Y-%H:%M:%S")

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    mutation= gql(
        """
            mutation {
                updateLowStockProducts {
                    updatedProducts {
                        name
                        stock
                    }
                    message
                }
            }
        """
    )

    try:
        response = client.execute(mutation)
        data = response.get("updateLowStockProducts", {})
        products = data.get("updatedProducts", [])
        message = data.get("message", "No message returned")

        with open(log_file, "a") as f:
            f.write(f"{timestamp} - {message}\n")
            for p in products:
                f.write(f"Updated: {p['name']} - New stock: {p['stock']}\n")
    
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - error updating low stock: {e}\n")