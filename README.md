# wiz-gcp-projectc-based-subs-tags
Assign GCP subscription based on labels to wiz Project

# IMPORTANT: update the bellow variables on main.py  before running the script. The following fields are currently empty and need to be updated:
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
The purpose of the script is to have dynamic adding of GCP subscriptions to Wiz Projects based on the GCP project labels. This is to make sure that all onboarded subscriptions are mapped to proper Wiz Projects automatically without manual intervention. The script can be run on a regular basis (e.g. daily) to constantly update the accounts.

## Usage:
- dry-run to test which projects will be created and which subscriptions will be added to the Wiz Project.
```
python3 main.py --dry-run yes
```
- Run the script.
```
python3 main.py
```
