########################################################################################################################
#These run on the host

setup:
	cp nanoHUB/.env.dev nanoHUB/.env

dev:
	git pull
	make dev-down
	make dev-up

pipeline-test:
	git pull
	make pipeline-down
	NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g)  CRONTAB_FILE=nanoHUB/scheduler/crontab.test docker-compose -f docker-compose-pipeline.yml up --build

pipeline-prod:
	git pull
	make pipeline-down
	NB_USER="$(whoami)" NB_UID="$(id -u)" NB_GID="$(id -g)" CRONTAB_FILE=nanoHUB/scheduler/crontab docker-compose -f docker-compose-pipeline.yml up --build


########################################################################################################################
# Base Commands

dev-down:
	docker-compose down

dev-up:
	NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g) docker-compose up --build

pipeline-down:
	docker-compose -f docker-compose-pipeline.yml down

########################################################################################################################
#These run inside the container

cron-log:
	tail -f /var/log/cron.log

show-cron_tasks:
	tail -f cron_tasks


########################################################################################################################
# Others

gcloud_ip=$(shell curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip)

gsetup: setup
	$(shell sed -i -e "/JUPYTER_DISPLAY_IP_ADDRESS/ a JUPYTER_DISPLAY_IP_ADDRESS='$(gcloud_ip)'" .env)

gcloud:
	git pull
	docker-compose down
	NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g) docker-compose up --build