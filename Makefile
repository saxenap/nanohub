

cron-log:
	tail -f /var/log/cron.log


jupyter-container:
	docker-compose run -p "8888:8888" --rm dev


pipeline-container:
	docker-compose -f docker-compose-pipeline.yml down && docker-compose -f docker-compose-pipeline.yml up


pipeline-test:
	export CRONTAB_FILE=nanoHUB/scheduler/crontab.test
	docker-compose -f docker-compose-pipeline.yml down
	docker-compose -f docker-compose-pipeline.yml up

pipeline-prod:
	export CRONTAB_FILE=nanoHUB/scheduler/crontab
	docker-compose -f docker-compose-pipeline.yml down
	docker-compose -f docker-compose-pipeline.yml up