if [ `docker ps | wc -l` = 4 ]
then
	exit 0
else
	exit 1
fi
