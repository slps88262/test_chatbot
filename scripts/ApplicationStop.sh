#!/bin/bash
if [ `docker ps | wc -l` > 1 ]
then
	cd /home/ec2-user/deploy
	docker-compose down
fi

if [`docker images | wc -l` > 1 ]
then
	docker image rm -f 204065533127.dkr.ecr.ap-northeast-1.amazonaws.com/chatbot_db:latest
	docker image rm -f 204065533127.dkr.ecr.ap-northeast-1.amazonaws.com/chatbot_flask:latest
	docker image rm -f 204065533127.dkr.ecr.ap-northeast-1.amazonaws.com/chatbot_serveo:latest
fi

exit 0
