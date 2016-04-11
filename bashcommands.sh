# A few environment variables have to be set, but many of them can be sourced from the openrc.sh file of OpenStack. These are $OS_TENANT_NAME, $OS_PASSWORD, $OS_REGION_NAME. $OS_TOKEN has to be set implicitly before use. The

# List all the services on the service manager
curl -v -X GET http://127.0.0.1:8888/-/ -H 'Accept: text/occi' -H 'X-Auth-Token: '$OS_TOKEN -H 'X-Tenant-Name: '$OS_TENANT_NAME

# With this command you can create a new instance
# the rootfolder and possibly the savetemplatetolocalpath have to be set
curl -v -X POST http://127.0.0.1:8888/haas/ -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H 'X-Auth-Token: '$OS_TOKEN -H 'X-Tenant-Name: '$OS_TENANT_NAME -H 'X-OCCI-Attribute: icclab.haas.debug.donotdeploy="False",icclab.haas.rootfolder="/Users/puenktli/Documents/Coding/PycharmProjects/hurtle_sm/dataLisa",icclab.haas.master.sshkeyname="MNMBA",icclab.haas.debug.savetemplatetolocalpath="/Users/puenktli/Desktop/currentTemplate.yaml",OS_TENANT_NAME="'$OS_TENANT_NAME'",OS_PASSWORD="'$OS_PASSWORD'",OS_REGION_NAME="'$OS_REGION_NAME'",OS_USERNAME="'$OS_USERNAME'"'

# List all the instances that are deployed for the service haas
curl -v -X GET http://127.0.0.1:8888/haas/ -H 'Accept: text/occi' -H 'X-Auth-Token: '$OS_TOKEN -H 'X-Tenant-Name: '$OS_TENANT_NAME

# List the details for the specific instance
# the URL has to be set accordingly
curl -v -X GET http://127.0.0.1:8888/haas/f91eb4b8-36f1-4ec2-816d-dfe6667c2979 -H 'Accept: text/occi' -H 'X-Auth-Token: '$OS_TOKEN -H 'X-Tenant-Name: '$OS_TENANT_NAME -H 'X-OCCI-Attribute: OS_TENANT_NAME="'$OS_TENANT_NAME'",OS_PASSWORD="'$OS_PASSWORD'",OS_REGION_NAME="'$OS_REGION_NAME'",OS_USERNAME="'$OS_USERNAME'"'

# With this command you delete the specific instance
# the URL has to be set accordingly
curl -v -X DELETE http://127.0.0.1:8888/haas/f91eb4b8-36f1-4ec2-816d-dfe6667c2979 -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H 'X-Auth-Token: '$OS_TOKEN -H 'X-Tenant-Name: '$OS_TENANT_NAME -H 'OS_TENANT_NAME="'$OS_TENANT_NAME'",OS_PASSWORD="'$OS_PASSWORD'",OS_REGION_NAME="'$OS_REGION_NAME'",OS_USERNAME="'$OS_USERNAME'",OS_PASSWORD="'$OS_PASSWORD'",OS_REGION_NAME="'$OS_REGION_NAME'",OS_USERNAME="'$OS_USERNAME'"'
