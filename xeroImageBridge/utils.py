# xeroImageBridge/scripts.py
import requests
import urllib.parse

def get_xero_ticket(jsf_user, xero_user, ticket_duration, xero_password, xero_server, xero_domain, query_constraints, display_vars):
    api_url = f"https://{xero_server}/encodedTicket"

    # URL encode the query constraints and display vars
    query_constraints_encoded = urllib.parse.quote(query_constraints)
    display_vars_encoded = urllib.parse.quote(display_vars)
    print(query_constraints_encoded)
    print(display_vars_encoded)
    payload = {
        "user": xero_user,
        "password": xero_password,
        "domain": xero_domain,
        "queryConstraints": query_constraints_encoded,
        "initialDisplay": display_vars_encoded,
        "ticketDuration": ticket_duration,
        "uriEncodedTicket": "true",
        "ticketUser": jsf_user,
        "ticketRoles": "EprUser",
    }

    headers = {
        #'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        print(api_url,headers, payload)
        response = requests.post(api_url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            print(f"ticket is: {response.text}")
            return response.text
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error creating Xero ticket: {e}")
        return None

def get_xero_ticket_get(jsf_user, xero_user, ticket_duration, xero_password, xero_server, xero_domain, query_constraints, display_vars):
    # URL encode the query constraints and display vars
    query_constraints_encoded = urllib.parse.quote(query_constraints)
    display_vars_encoded = urllib.parse.quote(display_vars)
    api_url = f"https://{xero_server}/encodedTicket?user={xero_user}&password={xero_password}&domain={xero_domain}&ticketUser={jsf_user}&ticketDuration={ticket_duration}&ticketRoles=EprUser&uriEncodedTicket=true&queryConstraints={query_constraints_encoded}&initialDisplay={display_vars_encoded}"


    print(api_url)
    payload = {}
    headers = {}

    try:
        print(api_url,headers, payload)
        response = requests.post(api_url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            print(f"ticket is: {response.text}")
            return response.text
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error creating Xero ticket: {e}")
        return None

