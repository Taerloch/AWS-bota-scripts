import boto3
import json
import csv
import datetime
import sys
from datetime import date
debug = True
def get_Workspaces(client, userInfos):
    paginator = client.get_paginator('describe_workspaces')
    
    i = 0
        
    for workspace in [workspaces  for page in paginator.paginate() for workspaces in page["Workspaces"]]:
        
        # PACCAR metadata is stored in tags, at this time I am only scraping division code
        tags = client.describe_tags(ResourceId = workspace["WorkspaceId"])["TagList"]
        division = [tag["Value"]  for tag in tags if tag['Key'] in ['div', 'Div']]
        
        # Need to prune workstation that have not been used.
        try:
            last_login = client.describe_workspaces_connection_status(WorkspaceIds = [workspace["WorkspaceId"]]).get("WorkspacesConnectionStatus",[{"LastKnownUserConnectionTimestamp" : "1/1/2020"}]).pop().get('LastKnownUserConnectionTimestamp', datetime.date(2030, 1, 1))
        except:
            last_login = datetime.date(2030, 1, 1)   
        #TODO: add in the timestamp of observation. and the region and department
        UserInfo = {
            'WorkspaceId' :  workspace["WorkspaceId"],\
            'UserName' : workspace["UserName"], \
            'Division' :  division[0] if division else "na",\
            'Contractor' : 'A-' in workspace['UserName'], 
            'Auto-Provisioned' : ['True','true'] in [tag2['Value']  for tag2 in tags if tag2['Key'] in ['AutoProvision']],\
            'ComputerName' :  workspace["ComputerName"], \
            'IpAddress' : workspace["IpAddress"], \
            'LastLogin' : last_login.strftime("%Y-%m-%d")

            }
       
        
        if debug : 
            
            print(UserInfo, end = '\r', flush = True)
       

        # userInfos.append(UserInfo)
        putinDyn(UserInfo)

# step to add the user information to the Workspaces Table
# dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
def putinDyn(UserInfo):
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

    
