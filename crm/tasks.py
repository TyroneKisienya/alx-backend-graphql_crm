from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import requests

@shared_task
def generate_crm_report():
    log_file = "/tmp/crm_report_log.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:&m;%s')

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql(
        """
            query {
            all customers {
                id
            }
            allOrders{
                id
                totalAmount
            }           
        }
        """
    )

    try:
        response = client.execute(query)
        customers = response.get('allCustomers', [])
        orders = response.get('allOrders', [])

        total_customers = len(customers)
        total_orders = len(orders)
        total_revenue = sum(order.get('total_amount', 0)for order in orders)

        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Report: {total_customers} customers,"
                    f"{total_orders} orders, {total_revenue} revenue\n"
                    )
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error generating report: {e}")