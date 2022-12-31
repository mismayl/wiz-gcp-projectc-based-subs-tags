# wiz-gcp-projectc-based-subs-tags
Assign GCP subscription based on labels to wiz Project

# IMPORTANT: update the main,py credentials, tags and project prefix variables before running the script. The following fields are currently empty and need to be updated:
This is the GraphQL API endpoint used by your tenant.
Learn more about this using the Wiz API
```
client_id --> introduce your Wiz  CLIENT ID
client_secret  --> introduce your Wiz  CLIENT SECRET
api_endpoint --> This is the GraphQL API endpoint used by your tenant.
tagkey --> The GCP label that should be used to map the GCP project to the Wiz Project
projectPrefix --> The profix to apped to the Wiz Project name
```

## Prerequisites:
- The script is tested on Python 3.10
- Install gql package
    
## Applicable use cases:

The purpose of the script is to have dynamic adding of GCP projects to Wiz Projects based on the GCP project labels. This is to make sure that all onboarded subscriptions are mapped to proper Wiz Projects automatically without manual intervention. The script can be run on a regular basis (e.g. daily) to constantly update the accounts.


