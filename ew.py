import boto3
import json
import csv
import datetime
import sys
from datetime import date
from time import sleep
debug = True
def get_Workspaces(client, userInfos):
    paginator = client.get_paginator('describe_workspaces')

    i = 0

    for workspace in [workspaces  for page in paginator.paginate() for workspaces in page["Workspaces"]]:

        # PACCAR metadata is stored in tags, at this time I am only scraping division code
        tags = client.describe_tags(ResourceId = workspace["WorkspaceId"])["TagList"]
        sleep (0.01)
        division = [tag.get("Value", 'na')  for tag in tags if tag['Key'] in ['div', 'Div']]
        department = [tag.get("Value", 'na')  for tag in tags if tag['Key'] in ['dept', 'Dept']]
        # Need to prune workstation that have not been used.
        try:
            last_login = client.describe_workspaces_connection_status(WorkspaceIds = [workspace["WorkspaceId"]]).get("WorkspacesConnectionStatus",[{"LastKnownUserConnectionTimestamp" : "1/1/2020"}]).pop().get('LastKnownUserConnectionTimestamp', datetime.date(2030, 1, 1))
        except:
            last_login = datetime.date(2030, 1, 1)
        #TODO: add in the timestamp of observation. and the region and department
        UserInfo = {
            'WorkspaceId' :  workspace["WorkspaceId"],\
            'UserName' : workspace.get("UserName", "NA"), \
            'User-Region': client.meta.region_name,\
            'Division' :  division[0] if division else "NA",\
            'Department' :  department[0] if department else "NA",\
            'Contractor' : 'A-' in workspace.get('UserName', "NA"),
            'Auto-Provisioned' : ['True','true'] in [tag2['Value']  for tag2 in tags if tag2['Key'] in ['AutoProvision']],\
            'ComputerName' :  workspace.get("ComputerName", "NA"), \
            'IpAddress' : workspace.get("IpAddress", "NA"), \
            'LastLogin' : last_login.strftime("%Y-%m-%d"),\
            'LastUpdate' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            }


        if debug :

            print(UserInfo, end = '\r', flush = True)


        userInfos.append(UserInfo)
        putinDyn(UserInfo)

# step to add the user information to the Workspaces Table
# dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
def putinDyn(UserInfo):
    table = dynamodb.Table('Workspaces')
    response = table.put_item( Item = UserInfo)


userInfos = []
regionNames = ['us-west-2', 'eu-central-1', 'ap-southeast-2']
for region in regionNames:
    get_Workspaces(boto3.client('workspaces', region_name=region), userInfos)

filename  = "workspaces" + date.today().isoformat() + ".csv"
with open (filename , 'w') as csv_file:
    fieldnames = ['WorkspaceId','UserName', 'Division', 'Contractor', 'Auto-Provisioned', 'ComputerName', 'IpAddress', 'LastLogin', 'LastUpdate', 'User-Region', 'Department' ]
    writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
    writer.writeheader()
    writer.writerows(userInfos)
