import boto3
import json
import csv
client = boto3.client('workspaces', region_name = 'eu-central-1')
paginator = client.get_paginator('describe_workspaces')

# for page in page_iterator:
# #    print (page["Workspaces"])
#     for workspaces in page["Workspaces"]:
#         UserInfo = (workspaces["UserName"], client.describe_tags(ResourceId = workspaces["WorkspaceId"]))
#         print (UserInfo)
i = 0
with open ('temp.csv' , 'w') as csv_file:
    fieldnames = ['UserName', 'Division', 'Contractor', 'Auto-Provisioned']
    writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
    writer.writeheader()
    for workspace in [workspaces  for page in paginator.paginate() for workspaces in page["Workspaces"]]:
    # print(workspace)
        i = i + 1
        tags = client.describe_tags(ResourceId = workspace["WorkspaceId"])["TagList"]
        #print (tags)
        division = [tag["Value"]  for tag in tags if tag['Key'] in ['div', 'Div']]
        UserInfo = {
         'UserName' : workspace["UserName"], \
         'Division' :  division[0] if division else "na",\
         'Contractor' : 'A-' in workspace['UserName'], 
         'Auto-Provisioned' : ['True','true'] in [tag2['Value']  for tag2 in tags if tag2['Key'] in ['AutoProvision']],\
         
         }
        print (UserInfo)
        writer.writerow(UserInfo)
    

    
    
