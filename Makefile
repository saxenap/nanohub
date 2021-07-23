########################################################################################################################
#These run on the host

setup:
	cp nanoHUB/.env.dev nanoHUB/.env

dev:
	git pull
	docker-compose down
	NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g) docker-compose up --build

pipeline-test:
	git pull
	docker-compose -f docker-compose-pipeline.yml down
	NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g)  CRONTAB_FILE=nanoHUB/scheduler/crontab.test docker-compose -f docker-compose-pipeline.yml up --build

pipeline-prod:
	git pull
	docker-compose -f docker-compose-pipeline.yml down
	NB_USER="$(whoami)" NB_UID="$(id -u)" NB_GID="$(id -g)" CRONTAB_FILE=nanoHUB/scheduler/crontab docker-compose -f docker-compose-pipeline.yml up --build

########################################################################################################################
#These run inside the container

cron-log:
	tail -f /var/log/cron.log

show-cron_tasks:
	tail -f cron_tasks


########################################################################################################################
# Others

gcloud_ip: $(shell curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip)
gcloud:
	git pull
	$(shell sed -i -e "/JUPYTER_DISPLAY_IP_ADDRESS/ a JUPYTER_DISPLAY_IP_ADDRESS=${gcloud_ip}" .env)
	docker-compose down
	NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g) docker-compose up --build