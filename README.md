# reporting-auth-client

* To show everyone in the whitelist, run the `client.py` script.
* To add someone to the whitelist:
  1. Request the new user to login to the Reportal, they will not have permission to view reporting information. This will create an entry into the ersa-account Datastore on GAE that contains their email address.
  2. Run the `grant_by_emailaddress.py` script by providing the email address for the person to add.
  3. The user will now be able to login again to the Reportal to see the reporting information for the institution their email address belongs to.
* To remove a user from the whitelist delete all of their entries in the Authorisation table on the ersa-account Datastore.

Access is granted per API endpoints (i.e. HPC and XFS data is served through two separate endpoints). In the case a new endpoint is created, then access to this endpoint will need to be applied again for everyone who needs access even if they are already on the whitelist.

__Credentials:__ Generated from GAE and copied to Keeper record named "reporting-auth-client".
