import boto3
import json
import csv
import datetime
from datetime import date
def get_Workspaces(client, userInfos):
    paginator = client.get_paginator('describe_workspaces')

    i = 0
        
    for workspace in [workspaces  for page in paginator.paginate() for workspaces in page["Workspaces"]]:
        # print(workspace)
        i = i + 1
        tags = client.describe_tags(ResourceId = workspace["WorkspaceId"])["TagList"]
        last_login = client.describe_workspaces_connection_status(WorkspaceIds = [workspace["WorkspaceId"]])["WorkspacesConnectionStatus"][0].get('LastKnownUserConnectionTimestamp', datetime.date(2030, 1, 1))
        division = [tag["Value"]  for tag in tags if tag['Key'] in ['div', 'Div']]
        UserInfo = {
        'WorkspaceId' :  workspace["WorkspaceId"],\
        'UserName' : workspace["UserName"], \
        'Division' :  division[0] if division else "na",\
        'Contractor' : 'A-' in workspace['UserName'], 
        'Auto-Provisioned' : ['True','true'] in [tag2['Value']  for tag2 in tags if tag2['Key'] in ['AutoProvision']],\
        'ComputerName' :  workspace["ComputerName"], \
        'IpAddress' : workspace["IpAddress"], \
        'LastLogin' : last_login.strftime("%m/%d/%Y, %H:%M:%S")

        }
        print (UserInfo)
        userInfos.append(UserInfo)
        putinDyn(UserInfo)
def putinDyn(UserInfo):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('Workspaces')
    response = table.put_item( Item = UserInfo)

          
userInfos = []
get_Workspaces(boto3.client('workspaces', region_name='us-west-2'), userInfos)
get_Workspaces(boto3.client('workspaces', region_name='eu-central-1'), userInfos)
get_Workspaces(boto3.client('workspaces', region_name='ap-southeast-2'), userInfos)

filename  = "workspaces" + date.today().isoformat() + ".csv"
with open (filename , 'w') as csv_file:
    fieldnames = ['WorkspaceId','UserName', 'Division', 'Contractor', 'Auto-Provisioned', 'ComputerName', 'IpAddress', 'LastLogin']
    writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
    writer.writeheader()
    writer.writerows(userInfos)

    
