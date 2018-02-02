import os
import sys
import datetime

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

def grant_all_access(client, account, endpoints):
    for endpoint in endpoints:
        grant_access(client, account, get_endpoint_key(endpoint))

def remove_all_access(client, account):
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
    print("%s has access to:" % account['name'])
    for access in query.fetch():
        endpoint = client.get(access['endpoint'])
        print(endpoint['name'])

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

if __name__ == '__main__':
    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        sys.exit('Please set env variable GOOGLE_APPLICATION_CREDENTIALS to your JSON file')

    # get projects list from gcloud
    # bin/gcloud projects list
    client = datastore.Client('ersa-reporting-auth')
    list_accesses(client)
