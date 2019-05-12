#!/bin/bash
cd /home/ec2-user/deploy/code/
aws s3 cp s3://dc101-project02/secretFile.txt .
cd /home/ec2-user/deploy/
aws s3 cp s3://dc101-project02/mysql_data.tar .
tar -xvf mysql_data.tar
rm mysql_data.tar

exit 0
