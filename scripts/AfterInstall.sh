#!/bin/bash -ex

#將sercretFile從s3下載
cd /home/ec2-user/deploy/code/
aws s3 cp s3://dc101-project02/secretFile.txt .

#將database從s3下載
cd /home/ec2-user/deploy/
aws s3 cp s3://dc101-project02/mysql_data.tar .
sudo tar -xvf mysql_data.tar
sudo rm mysql_data.tar

exit 0
~

