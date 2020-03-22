import boto3
import json
import csv
import datetime
client = boto3.client('workspaces', region_name='us-west-2')
paginator = client.get_paginator('describe_workspaces')

i = 0
with open (boto3.session.Session().region_name + '.csv' , 'w') as csv_file:
    fieldnames = ['UserName', 'Division', 'Contractor', 'Auto-Provisioned', 'ComputerName', 'IpAddress', 'LastLogin']
    writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
    writer.writeheader()
    for workspace in [workspaces  for page in paginator.paginate() for workspaces in page["Workspaces"]]:
    # print(workspace)
        i = i + 1
        tags = client.describe_tags(ResourceId = workspace["WorkspaceId"])["TagList"]
        status = client.describe_workspaces_connection_status(WorkspaceIds = [workspace["WorkspaceId"]])["WorkspacesConnectionStatus"][0].get('LastKnownUserConnectionTimestamp', datetime.date(2030, 1, 1))
        # last_login = status['LastKnownUserConnectionTimestamp'] if status else "Never"
        print (status)
        #print (tags)
        division = [tag["Value"]  for tag in tags if tag['Key'] in ['div', 'Div']]
        UserInfo = {
         'UserName' : workspace["UserName"], \
         'Division' :  division[0] if division else "na",\
         'Contractor' : 'A-' in workspace['UserName'], 
         'Auto-Provisioned' : ['True','true'] in [tag2['Value']  for tag2 in tags if tag2['Key'] in ['AutoProvision']],\
         'ComputerName' :  workspace["ComputerName"], \
         'IpAddress' : workspace["IpAddress"], \
         'LastLogin' : status

         }
        print (UserInfo)
        writer.writerow(UserInfo)
    


    
