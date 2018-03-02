import sys
from client import *

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("emailaddress is missing")

    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        sys.exit('Please set env variable GOOGLE_APPLICATION_CREDENTIALS to your JSON file')

    email = sys.argv[1]
    print("Will grant asscesses to %s" % email)

    # get projects list from gcloud
    # bin/gcloud projects list
    client = datastore.Client('ersa-reporting-auth')

    person = get_account_key(client, email)
    print("Found person by email %s" % person.key)

    endpoints = ('bman', 'hcp', 'hnas', 'hpc', 'nova', 'slurm', 'vms', 'xfs')
    print("Supported endpoints are:")
    print(*endpoints)

    grant_all_accesses(client, person, endpoints)
    for endpoint in endpoints:
        print("%s is accessible = %s" % (endpoint, verify_access(client, person, get_endpoint_key(client, endpoint))))

