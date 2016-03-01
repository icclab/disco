# List all the services on the service manager
curl -v -X GET http://127.0.0.1:8888/-/ -H 'Accept: text/occi' -H 'X-Auth-Token: a36ea8f7e0034b8c97a4f4323cd66d0d' -H 'X-Tenant-Name: saverio.proto@switch.ch'

#List all the instances that are deployed for the service haas
curl -v -X GET http://127.0.0.1:8888/haas/ -H 'Accept: text/occi' -H 'X-Auth-Token: a36ea8f7e0034b8c97a4f4323cd66d0d' -H 'X-Tenant-Name: saverio.proto@switch.ch'

#List the details for the specific instance
curl -v -X GET http://127.0.0.1:8888/haas/92a35fa8-00da-46d1-b33e-4da2ec3bad2c -H 'Accept: text/occi' -H 'X-Auth-Token: a36ea8f7e0034b8c97a4f4323cd66d0d' -H 'X-Tenant-Name: saverio.proto@switch.ch' -H 'X-OCCI-Attribute: sofloatingip="160.85.4.205"'

# With this command you can create a new instance
you will need:
neutron floatingip-list
for the id of the floating IP

curl -v -X POST http://127.0.0.1:8888/haas/ -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H 'X-Auth-Token: a36ea8f7e0034b8c97a4f4323cd66d0d' -H 'X-Tenant-Name: saverio.proto@switch.ch' -H 'X-OCCI-Attribute: icclab.haas.debug.donotdeploy="False",icclab.haas.master.createvolumeforattachment="False",sofloatingipid="88c433a4-319e-4e7b-828d-103ba9721455",sofloatingip="86.119.39.30",icclab.haas.rootfolder="/root/testso/bundle/data",icclab.haas.master.sshkeyname="macsp"'

# With this command you delete the specific intance
curl -v -X DELETE http://127.0.0.1:8888/haas/92a35fa8-00da-46d1-b33e-4da2ec3bad2c -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H 'X-Auth-Token: a36ea8f7e0034b8c97a4f4323cd66d0d' -H 'X-Tenant-Name: saverio.proto@switch.ch' -H 'X-OCCI-Attribute: icclab.haas.sm.sofloatingip="160.85.4.205"'
