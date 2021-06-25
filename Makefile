
#These run inside the container
cron-log:
	tail -f /var/log/cron.log

show-cron_tasks:
	tail -f cron_tasks

########################################################################################################################

#These run on the host
jupyter-container:
	docker-compose run -p "8888:8888" --rm dev

pipeline-container:
	docker-compose -f docker-compose-pipeline.yml down && docker-compose -f docker-compose-pipeline.yml up

pipeline-test:
	docker-compose -f docker-compose-pipeline.yml down
	export CRONTAB_FILE=nanoHUB/scheduler/crontab.test && docker-compose -f docker-compose-pipeline.yml up --build

pipeline-prod:
	docker-compose -f docker-compose-pipeline.yml down
	export CRONTAB_FILE=nanoHUB/scheduler/crontab && docker-compose -f docker-compose-pipeline.yml up --build