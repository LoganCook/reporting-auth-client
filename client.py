import os
import sys
import datetime
import json
import argparse

from google.cloud import datastore

def get_keyof(client, kind, key_filter):
    # if not find, there will be IndexError: list index out of range
    query = client.query(kind=kind)
    query.add_filter(*key_filter)
    query.keys_only()
    return list(query.fetch())[0]

def get_endpoint_key(client, endpoint):
    """Get the key of an Endpoint by its name"""
    return get_keyof(client, 'Endpoint', ('name', '=', endpoint))

def get_account_key(client, email):
    """Get the key of an Account by its name"""
    return get_keyof(client, 'Account', ('email', '=', email))

def grant_access(client, account, endpoint):
    """Link an Account and an Endpoint in Authorisation"""
    key = client.key('Authorisation')
    authorisation = datastore.Entity(key)
    authorisation['account'] = account.key
    authorisation['endpoint'] = endpoint.key
    authorisation['timestamp'] = datetime.datetime.utcnow()
    client.put(authorisation)
    return authorisation.key

def grant_all_accesses(client, account, endpoints):
    for endpoint in endpoints:
        grant_access(client, account, get_endpoint_key(client, endpoint))

def remove_all_accesses(client, account):
    query = client.query(kind='Authorisation')
    query.add_filter('account', '=', account.key)
    for access in query.fetch():
        client.delete(access.key)

def list_accesses(client):
    query = client.query(kind='Account')
    for account in query.fetch():
        get_accessess(client, account)

def get_accessess(client, account):
    query = client.query(kind='Authorisation')
    query.add_filter('account', '=', account.key)
    print("%s (%s) has access to:" % (account['name'], account['email']))
    empty = True
    for access in query.fetch():
        empty = False
        endpoint = client.get(access['endpoint'])
        print(endpoint['name'])
    if empty:
        print("<None>")
    print()

def verify_access(client, account, endpoint):
    """Verify if an Account has access of an Endpoint"""
    # both need to be key
    query = client.query(kind='Authorisation')
    query.add_filter('account', '=', account.key)
    query.add_filter('endpoint', '=', endpoint.key)
    return len(list(query.fetch())) > 0

def batch_grant(client, endpoint_name):
    """Grant access to an Endpoint to all accounts if they don't have yet"""
    endpoint = get_endpoint_key(client, endpoint_name)
    query = client.query(kind='Account')
    for account in query.fetch():
        if not verify_access(client, account, endpoint):
            print("Granting access to %s on %s" % (account['name'], endpoint_name))
            grant_access(client, account, endpoint)

def get_endpoints(client):
    endpoints = []
    query = client.query(kind='Endpoint')
    for endpoint in query.fetch():
        endpoints.append(endpoint['name'])
    return endpoints



if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Help administrate the reporting whitelist for users. Note that the Datastore can be manually edited on Google Cloud Platform.')
    parser.add_argument('--list', help='List all user accesses', action='store_true')
    parser.add_argument('--grant-user-all', help='Grant access to all API endpoints for a user', type=str, metavar="EMAIL")
    args = parser.parse_args()

    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        sys.exit('Please set env variable GOOGLE_APPLICATION_CREDENTIALS to your JSON file')

    # Parse credentials file to get project ID
    with open(os.environ['GOOGLE_APPLICATION_CREDENTIALS']) as file:
        data = json.load(file)
    project_id = data['project_id']
    print("Connecting to '%s'...\n" % project_id)

    # get projects list from gcloud
    # bin/gcloud projects list
    client = datastore.Client(project_id)

    endpoints = get_endpoints(client)
    print("Supported endpoints are:")
    print("\n".join(endpoints), "\n")

    if args.grant_user_all is not None:
        email = args.grant_user_all
        person = get_account_key(client, email)
        print("Found their key:\n%s\n\nAdding access..." % person.key)
        grant_all_accesses(client, person, endpoints)
        for endpoint in endpoints:
            print("%s is accessible = %s" % (endpoint, verify_access(client, person, get_endpoint_key(client, endpoint))))

    if args.list:
        print("Listing all user accesses...\n")
        list_accesses(client)
