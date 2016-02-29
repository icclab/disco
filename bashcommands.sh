curl -v -X GET http://127.0.0.1:8888/-/ -H 'Accept: text/occi' -H 'X-Auth-Token: 48b3517b6cf34e0d8d21882c036f44a8' -H 'X-Tenant-Name: mesz'

curl -v -X GET http://127.0.0.1:8888/haas/ -H 'Accept: text/occi' -H 'X-Auth-Token: 48b3517b6cf34e0d8d21882c036f44a8' -H 'X-Tenant-Name: mesz'

curl -v -X GET http://127.0.0.1:8888/haas/92a35fa8-00da-46d1-b33e-4da2ec3bad2c -H 'Accept: text/occi' -H 'X-Auth-Token: 48b3517b6cf34e0d8d21882c036f44a8' -H 'X-Tenant-Name: mesz' -H 'X-OCCI-Attribute: sofloatingip="160.85.4.205"'

curl -v -X POST http://127.0.0.1:8888/haas/ -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H 'X-Auth-Token: 48b3517b6cf34e0d8d21882c036f44a8' -H 'X-Tenant-Name: mesz' -H 'X-OCCI-Attribute: icclab.haas.debug.donotdeploy="False",icclab.haas.master.createvolumeforattachment="False",sofloatingipid="c03eb859-99f7-49f7-9316-dffd5af8c299",sofloatingip="160.85.4.205",icclab.haas.rootfolder="/root/testso/bundle/data",icclab.haas.master.sshkeyname="MNMBA2"'


curl -v -X DELETE http://127.0.0.1:8888/haas/92a35fa8-00da-46d1-b33e-4da2ec3bad2c -H 'Category: haas; scheme="http://schemas.cloudcomplab.ch/occi/sm#"; class="kind";' -H 'content-type: text/occi' -H 'X-Auth-Token: 48b3517b6cf34e0d8d21882c036f44a8' -H 'X-Tenant-Name: mesz' -H 'X-OCCI-Attribute: icclab.haas.sm.sofloatingip="160.85.4.205"'