# reporting-auth-client

A [credential file](https://cloud.google.com/docs/authentication/getting-started) needs to be exported for the client to communicate to the Google Cloud Datastore. The client user interface can list and add access to all API endpoints for a user given their email address, see `python client.py --help`.

To add someone to the whitelist:
1. Request the new user to login to the Reportal, they will not have permission to view reporting information. This will create an entry into the Datastore that contains their email address.
2. Use the client to then grant access using their email.
3. The user will now be able to login again to the Reportal to see their reporting information.

## Notes
* Not all functions have been exposed to the client interface yet.
* To remove user access, delete all of their entries in the Authorisation table.
* Access is granted per API endpoints (i.e. HPC and XFS data is served through two separate endpoints). In the case a new endpoint is created, then access to this endpoint will need to be applied again for everyone who needs access even if they are already on the whitelist.
* The credential file is also stored in Keeper under the record named "reporting-auth-client".
