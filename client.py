import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./auth_client-edd7b690c2e5.json"
# get projects list from gcloud
# bin/gcloud projects list

import datetime
from google.cloud import datastore
client = datastore.Client('ersa-reporting-auth')

query = client.query(kind='Endpoint')
list(query.fetch())


query = client.query(kind='Account', projection=('name',))
accounts = list(query.fetch())
for account in accounts:
    print(account['name'], account.key)

karl.key
ent_karl = client.get(karl.key)


account_query = client.query(kind='Account', projection=('email', 'timestamp'))
account_query.add_filter('name', '=', 'Karl Sellmann')

def get_keyof(client, kind, key_filter):
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
            print("Granting access to %s on %s" % (account['name'], endpoint))
            grant_access(client, account, endpoint)
