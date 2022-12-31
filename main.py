import http.client
import json
import os
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


client_id = ""
client_secret = ""
api_endpoint = ""
auth_endpoint = "auth.app.wiz.io"
tagkey = ""
projectPrefix = ""

def request_wiz_api_token(client_id, client_secret):
    """Retrieve an OAuth access token to be used against Wiz API"""
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    payload = (f"grant_type=client_credentials&client_id={client_id}"
               f"&client_secret={client_secret}&audience=beyond-api")

    conn = http.client.HTTPSConnection(auth_endpoint)
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    token_str = res.read().decode("utf-8")
    return json.loads(token_str)["access_token"]

def getSubs_wiz_api(access_token):
    query = gql("""
        query GraphSearch(
            $query: GraphEntityQueryInput
            $controlId: ID
            $projectId: String!
            $first: Int
            $after: String
            $fetchTotalCount: Boolean!
            $quick: Boolean
        ) {
            graphSearch(
            query: $query
            controlId: $controlId
            projectId: $projectId
            first: $first
            after: $after
            quick: $quick
            ) {
            totalCount @include(if: $fetchTotalCount)
            maxCountReached @include(if: $fetchTotalCount)
            pageInfo {
                endCursor
                hasNextPage
            }
            nodes {
                entities {
                id
                name
                type
                properties
                originalObject
                }
            }
            }
        }
    """)

    variables = {
                "first": 100,
                "query": {
                    "type": [
                        "SUBSCRIPTION"
                    ],
                    "select": True,
                    "where": {
                        "cloudPlatform": {
                            "EQUALS": [
                                "GCP"
                            ]
                        },
                        "tags": {
                            "TAG_CONTAINS_ALL": [
                            {
                                "key": tagkey
                            }
                            ]
                        }
                    }
                },
                "projectId": "*",
                "fetchTotalCount": True,
                "quick": False
                    
                }
    transport = AIOHTTPTransport(
        url=api_endpoint,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    client = Client(transport=transport, fetch_schema_from_transport=False,
                    execute_timeout=55)
    print("Getting Subscriptions list")
    result = client.execute(query, variable_values=variables)
    subs_nodes = result['graphSearch']['nodes']
    while (result['graphSearch']['pageInfo']['hasNextPage']):
        print("There is more to fetch, getting more data... (paginating)")
        variables['after'] = result['graphSearch']['pageInfo']['endCursor']
        try:
            result = client.execute(query, variable_values=variables)
            if result['graphSearch']['nodes'] is not None:
                subs_nodes += (result['graphSearch']['nodes'])
        except Exception as e:
            if ('502: Bad Gateway' not in str(e)
                    and '503: Service Unavailable' not in str(e)):
                print("<p>WizIngestion-Error: %s</p>" % str(e))
                break
            else:
                print("Retry")

    return subs_nodes


def getProjects_wiz_api(access_token):
    query = gql("""
        query GraphSearch(
            $query: GraphEntityQueryInput
            $controlId: ID
            $projectId: String!
            $first: Int
            $after: String
            $fetchTotalCount: Boolean!
            $quick: Boolean
        ) {
            graphSearch(
            query: $query
            controlId: $controlId
            projectId: $projectId
            first: $first
            after: $after
            quick: $quick
            ) {
            totalCount @include(if: $fetchTotalCount)
            maxCountReached @include(if: $fetchTotalCount)
            pageInfo {
                endCursor
                hasNextPage
            }
            nodes {
                entities {
                id
                name
                }
            }
            }
        }
    """)

    variables = {
                "first": 100,
                "query": {
                    "type": [
                        "PROJECT"
                    ],
                    "select": True
                },
                "projectId": "*",
                "fetchTotalCount": True,
                "quick": False
                    
                }
    transport = AIOHTTPTransport(
        url=api_endpoint,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    client = Client(transport=transport, fetch_schema_from_transport=False,
                    execute_timeout=55)
    print("Getting Projects list")
    result = client.execute(query, variable_values=variables)
    project_nodes = result['graphSearch']['nodes']
    while (result['graphSearch']['pageInfo']['hasNextPage']):
        print("There is more to fetch, getting more data... (paginating)")
        variables['after'] = result['graphSearch']['pageInfo']['endCursor']
        try:
            result = client.execute(query, variable_values=variables)
            if result['graphSearch']['nodes'] is not None:
                project_nodes += (result['graphSearch']['nodes'])
        except Exception as e:
            if ('502: Bad Gateway' not in str(e)
                    and '503: Service Unavailable' not in str(e)):
                print("<p>WizIngestion-Error: %s</p>" % str(e))
                break
            else:
                print("Retry")

    return project_nodes

def getProject_based_name_wiz_api(access_token, project_name):
    getProjectsquery = gql("""
        query ProjectsTable(
            $filterBy: ProjectFilters
            $first: Int
            $after: String
            $orderBy: ProjectOrder
        ) {
            projects(
            filterBy: $filterBy
            first: $first
            after: $after
            orderBy: $orderBy
            ) {
            nodes {
                id
                name
                cloudAccountLinks {
                    cloudAccount {
                    id
                    }
                    environment
                    shared
                }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
            totalCount
            }
        }
        """)
    getProjectsvariables = {
        "first": 500,
        "filterBy": {
            "search": project_name
        },
        "orderBy": {
            "field": "SECURITY_SCORE",
            "direction": "ASC"
        }
    }

    transport = AIOHTTPTransport(
        url=api_endpoint,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    client = Client(transport=transport, fetch_schema_from_transport=False,
                    execute_timeout=55)

    result = client.execute(getProjectsquery,
                            variable_values=getProjectsvariables)

    projects_with_p_name_in_them = result['projects']['nodes']
    exact_match_projects  = []
    for p in projects_with_p_name_in_them:
        if p['name'] == project_name:
            exact_match_projects.append(p)

    return exact_match_projects

def createProject_wiz_api(access_token, p_name):
    createProjectsquery = gql("""
        mutation CreateProject($input: CreateProjectInput!) {
        createProject(input: $input) {
            project {
            id
            }
        }
        }
    """)

    createProjectsvariables = {
        "input": {
            "name": p_name,
            "identifiers": [],
            "cloudOrganizationLinks": [],
            "repositoryLinks": [],
            "description": "",
            "securityChampions": [],
            "projectOwners": [],
            "businessUnit": "",
            "riskProfile": {
                "businessImpact": "MBI",
                "hasExposedAPI": "YES",
                "hasAuthentication": "UNKNOWN",
                "isCustomerFacing": "NO",
                "isInternetFacing": "YES",
                "isRegulated": "YES",
                "sensitiveDataTypes": [],
                "storesData": "YES",
                "regulatoryStandards": []
            }
        }
    }

    transport = AIOHTTPTransport(
        url=api_endpoint,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    client = Client(transport=transport, fetch_schema_from_transport=False,
                    execute_timeout=55)

    result = client.execute(createProjectsquery,
                            variable_values=createProjectsvariables)

    return result


def addSubToProject_via_wiz_api(access_token, projectId, cloudAccounts_list):
    query = gql("""
    mutation UpdateProject($input: UpdateProjectInput!) {
        updateProject(input: $input) {
            project {
            id
            }
        }
        }
    """)

    variables = {
        'input': {
            'id': projectId,
            'patch': {
                'cloudAccountLinks': cloudAccounts_list
            }
        }
    }

    transport = AIOHTTPTransport(url=api_endpoint,
                                 headers={'Authorization': 'Bearer ' + access_token})  # noqa: E501
    client = Client(transport=transport, fetch_schema_from_transport=False,
                    execute_timeout=55)

    result = client.execute(query, variable_values=variables)

    return result

def ifProject_exist(projectNodes,projectName):
    exist = False
    for project in projectNodes:
        if projectName == project['entities'][0]['name']:
            exist = True
            return exist
    return exist


def getSubs_tagValue(subs_nodes):
    subs_list = []
    tagValue_list =[]
    for sub in subs_nodes:
        subs_tags = {'name': sub['entities'][0]['name'],'id': sub['entities'][0]['id'],
            tagkey: sub['entities'][0]['properties']['tags'][tagkey]}
        tagValue_list.append (sub['entities'][0]['properties']['tags'][tagkey])
        subs_list.append (subs_tags)
    return subs_list,list(set(tagValue_list))

def main():
    token = request_wiz_api_token(client_id, client_secret)
    subs_nodes = getSubs_wiz_api(token)
    project_nodes = getProjects_wiz_api(token)

    for tag_value in getSubs_tagValue(subs_nodes)[1]:
        project_name= projectPrefix+tag_value
        if ifProject_exist(project_nodes,project_name):
            print ("Project "+project_name+" exist")
        else:
            print ("Creating project "+project_name)
            createProject_wiz_api(token,project_name)

    for sub in getSubs_tagValue(subs_nodes)[0]:
        project_name = projectPrefix+sub[tagkey]
        project = getProject_based_name_wiz_api(token,project_name)
        cloudAccounts_list= [{'cloudAccount': link['cloudAccount']['id'],'environment':link['environment'],'shared':link['shared']}   for link in project[0]['cloudAccountLinks']]
        if sub ['id'] in [cloudAccount['cloudAccount'] for cloudAccount in cloudAccounts_list]:
            print ("Subscription "+sub['name']+" is already assigned to project "+project_name)
            addSubToProject_via_wiz_api(token, project[0]['id'], cloudAccounts_list)
        else:
            cloudAccounts_list.append({'cloudAccount': sub['id'],'environment': 'PRODUCTION','shared': False})
            print ("adding subscription "+sub['name']+" to project "+project_name)
            addSubToProject_via_wiz_api(token, project[0]['id'], cloudAccounts_list)





if __name__ == '__main__':
    main()
