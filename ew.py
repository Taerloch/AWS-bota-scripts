import boto3
import json
client = boto3.client('workspaces', region_name = 'eu-central-1')
paginator = client.get_paginator('describe_workspaces')

page_iterator = paginator.paginate()
for page in page_iterator:
#    print (page["Workspaces"])
    for workspaces in page["Workspaces"]:
        UserInfo = (workspaces["UserName"], client.describe_tags(ResourceId = workspaces["WorkspaceId"]))
        print (UserInfo)
