########################################################################################################################
#These run on the host


dev:
	git pull
	docker-compose down
	docker-compose up --build

pipeline-test:
	git pull
	docker-compose -f docker-compose-pipeline.yml down
	CRONTAB_FILE=nanoHUB/scheduler/crontab.test docker-compose -f docker-compose-pipeline.yml up --build

pipeline-prod:
	git pull
	docker-compose -f docker-compose-pipeline.yml down
	CRONTAB_FILE=nanoHUB/scheduler/crontab docker-compose -f docker-compose-pipeline.yml up --build

########################################################################################################################
#These run inside the container

cron-log:
	tail -f /var/log/cron.log

show-cron_tasks:
	tail -f cron_tasks