import boto3
import json
client = boto3.client('workspaces', region_name = 'us-west-2')
paginator = client.get_paginator('describe_workspaces')

# for page in page_iterator:
# #    print (page["Workspaces"])
#     for workspaces in page["Workspaces"]:
#         UserInfo = (workspaces["UserName"], client.describe_tags(ResourceId = workspaces["WorkspaceId"]))
#         print (UserInfo)
i = 0
for workspace in [workspaces  for page in paginator.paginate() for workspaces in page["Workspaces"]]:
    # print(workspace)
    i = i + 1
    UserInfo = (workspace["UserName"], [tag['Value']  for tag in client.describe_tags(ResourceId = workspace["WorkspaceId"])["TagList"] if tag['Key'] in ['div', 'dept']])
    print (UserInfo, i)
    
