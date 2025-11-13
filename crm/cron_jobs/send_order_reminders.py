#!/bin/python3

from datetime import timedelta, datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import sys

LOG_FILE="/tmp/order_reminders_log.txt"

def log_message(message: str):
    with open(LOG_FILE, "a")as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def main():
    seven_days_ago= (datetime.now() - timedelta(days=7)).strftime('%Y-%M-%D')

    transport= RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )

    client= Client(transport=transport, fetch_schema_from_transport=False)

    query= gql(
        """
            query GetRecentPendingOrders($since: Date!) {
                orders(order_date: $since, status: "PENDING") {
                    id
                    customer {
                        email
                    }
                }
            }
        """
    )

    try:
        response= client.execute(query, variable_value={"since": seven_days_ago})
        orders= response.get('orders', [])

        if not orders:
            log_message("No pending orders in the last seven days")
        else:
            for order in orders:
                order_id = order.get("id")
                customer_email= order.get("customer", {}).get("email")
                log_message(f"Pending Order ID: {order_id}, customer email: {customer_email}")
        
        print("order reminders processed")

    except Exception as e:
        log_message(f"Error while fetching orders: {str(e)}")
        print("Check log file, execution failed")
        sys.exit(1)

if __name__ == "__main__":
    main()