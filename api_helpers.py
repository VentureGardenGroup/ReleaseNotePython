import json

import os
import requests
from dateutil.parser import parse as date_parser

JIRA_API_KEY = os.getenv('JIRA_API_KEY')
OCTOPUS_API_KEY = os.getenv('OCTOPUS_API_KEY')
JIRA_URL = os.getenv("JIRA_URL")
OCTOPUS_URL = os.getenv("OCTOPUS_URL")


def get_release_notes(project_id, release_version, release_date, release_summary, tickets):
    api_base_url = JIRA_URL
    issue_endpoint = 'rest/api/2/issue/{0}'
    headers = {'Content-Type': 'application/json',
               'Authorization': "Basic {0}".format(JIRA_API_KEY)}
    tickets = tickets.split(',')
    request = requests.Session()
    try:
        print '{0} - Release Notes'.format(project_id)
        print "Release version {0} - {1}".format(release_version, release_date)
        print release_summary
        print 'Number of Issues in this release {0}'.format(len(tickets))
        print ''
        for ticket in tickets:
            response = request.get(api_base_url + issue_endpoint.format(ticket), headers=headers)
            if response.status_code == requests.codes.ok:
                d = response.json()
                print "Issue -> {0}".format(ticket)
                print 'Issue Summary -> {0}'.format(d['fields']['summary'])
                print 'Issue Description -> {0}'.format(d['fields']['description'])
                print 'Issue Type -> {0}'.format(d['fields']['issuetype']['name'])
                print 'Issue Status -> {0}'.format(d['fields']['status']['name'])
                print ''
    except Exception as e:
        print(e)


def get_all_jira_projects():
    api_base_url = JIRA_URL
    issue_endpoint = 'rest/api/2/project/'
    headers = {'Content-Type': 'application/json',
               'Authorization': "Basic {0}".format(JIRA_API_KEY)}
    request = requests.Session()
    try:
        response = request.get(api_base_url + issue_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            projects = response.json()
            if projects:
                projects = [{'key': project.get('key'),
                             'name': project['name'],
                             'id': project['id']} for project in projects]
            return projects
    except Exception as e:
        print(e)
    return None


def get_jira_project(project_id):
    api_base_url = JIRA_URL
    issue_endpoint = 'rest/api/2/project/{0}'.format(project_id)
    headers = {'Content-Type': 'application/json',
               'Authorization': "Basic {0}".format(JIRA_API_KEY)}
    request = requests.Session()
    try:
        response = request.get(api_base_url + issue_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            project = response.json()
            if project:
                project = {'key': project.get('key'),
                           'name': project['name'],
                           'id': project['id'],
                           'description': project['description']}
            return project
    except Exception as e:
        print(e)
    return None


def get_jira_ticket(ticket_id):
    api_base_url = JIRA_URL
    issue_endpoint = 'rest/api/2/issue/{0}'.format(ticket_id)
    headers = {'Content-Type': 'application/json',
               'Authorization': "Basic {0}".format(JIRA_API_KEY)}
    request = requests.Session()
    try:
        response = request.get(api_base_url + issue_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            ticket = response.json()
            if ticket:
                ticket = dict(key=ticket.get('key'), summary=ticket['fields']['summary'],
                              description=ticket['fields']['description'],
                              issue_type=ticket['fields']['issuetype']['name'],
                              status_name=ticket['fields']['status']['name'])
                return ticket
    except Exception as e:
        print(e)
    return None


def get_all_octopus_projects():
    api_base_url = OCTOPUS_URL
    projects_endpoint = 'api/projects/all'
    headers = {'Content-Type': 'application/json', 'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    request = requests.Session()
    try:
        response = request.get(api_base_url + projects_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            items = response.json()
            if items:
                projects = [dict(id=item.get('Id'), name=item.get('Name'), slug=item.get('Slug'),
                                 description=item.get('Description')) for item in items]
            return projects
    except Exception as e:
        print (e)
    return None


def get_octopus_project_releases(project_slug_or_id):
    api_base_url = OCTOPUS_URL
    releases_endpoint = 'api/projects/{0}/releases'.format(project_slug_or_id)
    headers = {'Content-Type': 'application/json', 'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    request = requests.Session()
    try:
        response = request.get(api_base_url + releases_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            results = response.json()
            items = results.get("Items")
            if items:
                releases = [dict(id=item.get('Id'), version=item.get('Version'),
                                 assembled=date_parser(item.get('Assembled')).strftime("%d %B, %Y %I:%M %p"),
                                 release_notes=item.get('ReleaseNotes'), project_id=item.get('ProjectId'),
                                 channel_id=item.get('ChannelId')) for item in
                            items]
            return releases
    except Exception as e:
        print (e)
    return None


def get_octopus_release(release_id):
    api_base_url = OCTOPUS_URL
    release_endpoint = 'api/releases/{0}'.format(release_id)
    headers = {'Content-Type': 'application/json', 'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    request = requests.Session()
    try:
        response = request.get(api_base_url + release_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            item = response.json()
            if item:
                release = dict(id=item.get('Id'), version=item.get('Version'),
                               assembled=date_parser(item.get('Assembled')).strftime("%d %B, %Y %I:%M %p"),
                               release_notes=item.get('ReleaseNotes'), project_id=item.get('ProjectId'),
                               channel_id=item.get('ChannelId'),
                               selected_packages=item.get('SelectedPackages'))
            return release
    except Exception as e:
        print (e)
    return None


def edit_octopus_release_note(release_id, version, channel_id, release_notes, selected_packages):
    api_base_url = OCTOPUS_URL
    create_release_endpoint = 'api/releases/{0}'.format(release_id)
    headers = {'Content-Type': 'application/json', 'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    request = requests.Session()
    try:
        response = request.put(api_base_url + create_release_endpoint, headers=headers, data=json.dumps(
            dict(Version=version, ChannelId=channel_id, ReleaseNotes=release_notes, Id=release_id,
                 SelectedPackages=selected_packages)))
        if response.status_code == requests.codes.ok:
            result = response.json()
            if result:
                return 'LastModifiedOn' in result
    except Exception as e:
        print(e)
    return False


def get_octopus_project(project_id):
    api_base_url = OCTOPUS_URL
    project_endpoint = 'api/projects/{0}'.format(project_id)
    headers = {'Content-Type': 'application/json', 'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    request = requests.Session()
    try:
        response = request.get(api_base_url + project_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            item = response.json()
            if item:
                project = dict(id=item.get('Id'), name=item.get('Name'), slug=item.get('Slug'),
                               description=item.get('Description'))
            return project
    except Exception as e:
        print (e)
    return None


def get_octopus_dashboard():
    api_base_url = OCTOPUS_URL
    dashboard_endpoint = 'api/dashboard'
    headers = {'Content-Type': 'application/json', 'X-Octopus-ApiKey': OCTOPUS_API_KEY}
    request = requests.Session()
    try:
        response = request.get(api_base_url + dashboard_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            results = response.json()
            projects = results.get('Projects')
            items = results.get('Items')
            if items and projects:
                prepared_projects = []
                new_items = {}
                for item in items:
                    new_items[item.get('ProjectId')] = item
                new_projects = {}
                for project in projects:
                    new_projects[project.get('Id')] = project
                for key, value in new_projects.iteritems():
                    item = dict(id=value.get('Id'), name=value.get('Name'), slug=value.get('Slug'),
                                description=value.get('Description'))
                    data = new_items.get(key)
                    release_version = ''
                    state = ''
                    created = ''
                    release_id = ''
                    if data:
                        release_version = data.get('ReleaseVersion')
                        state = data.get('State')
                        created = date_parser(data.get('Created')).strftime("%d %B, %Y %I:%M %p")
                        release_id = data.get('ReleaseId')
                    item['release_version'] = release_version
                    item['state'] = state
                    item['created'] = created
                    item['release_id'] = release_id
                    prepared_projects.append(item)
            return prepared_projects
    except Exception as e:
        print (e)
    return None


def get_jira_project_issues(project_id_or_slug):
    api_base_url = JIRA_URL
    issue_endpoint = 'rest/api/2/search?jql=project={0}&fields=id,key,summary,description,issuetype,status'.format(
        project_id_or_slug)
    headers = {'Content-Type': 'application/json',
               'Authorization': "Basic {0}".format(JIRA_API_KEY)}
    request = requests.Session()
    try:
        response = request.get(api_base_url + issue_endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            issue_response = response.json()
            issue_response = issue_response.get('issues')
            issues = []
            if issue_response:
                for issue in issue_response:
                    ticket = dict(key=issue.get('key'),
                                  summary=issue['fields']['summary'],
                                  description=issue['fields']['description'],
                                  issue_type=issue['fields']['issuetype']['name'],
                                  status_name=issue['fields']['status']['name'])
                    issues.append(ticket)
            return issues
    except Exception as e:
        print(e)
    return []


def get_jira_project_id_or_slug(octopus_id_name):
    projects = {
        'Projects-66': 'BDA',
        'Projects-26': 'BDA',
        'Projects-70': 'BDA',
        'Projects-62': 'BDA',
        'Projects-141': 'DEMO',
        'Projects-77': 'SPRYTE',
        'Projects-78': 'SPRYTE',
        'Projects-73': '',
        'Projects-102': 'AMR',
        'Projects-182': 'AV',
        'Projects-41': 'TSC',
        'Projects-61': 'TSC',
        'Projects-21': 'FID',
        'Projects-69': 'FID',
        'Projects-28': 'FID',
        'Projects-124': '',
        'Projects-81': '',
        'Projects-161': '',
        'Projects-76': '',
        'Projects-24': 'POW',
        'Projects-86': 'PMD',
        'Projects-72': 'PPY',
        'Projects-67': 'PPY',
        'Projects-75': 'VPOC',
        'Projects-183': '',
        'Projects-82': 'VAT'
    }
    return projects.get(octopus_id_name)

# print get_jira_project_issues("BDA")

# print get_octopus_dashboard()

# print get_all_jira_projects()

# print get_jira_project("10404")

# print get_jira_ticket("BDA-19")

# get_release_notes('BDA', '1.6.0-beta1', datetime.now(), 'BDA Release Summary',
#                 'BDA-19,BDA-18,BDA-13,BDA-12,BDA-10,BDA-11')


# projects_ = get_all_octopus_projects()

# for project_ in projects_:
#     print project_.get('name')
#     releases_ = get_octopus_project_releases(project_.get('id'))
#     for release_ in releases_:
#         print release_
#     print ''

# print get_octopus_project_release("Releases-1186")

# print edit_octopus_release_note(release_id='Releases-1186', version='0.0.1', channel_id='Channels-127',
#                               release_notes="this is the first release; Updated Again")
