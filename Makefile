env-vars=NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g) CPUS=$$(getconf _NPROCESSORS_ONLN)

log-level=INFO
########################################################################################################################
#These run on the host

setup:
	cp nanoHUB/.env.dev nanoHUB/.env

dev:
	git pull
	make dev-down
	make dev-up

pipeline:
	git pull
	make pipeline-down
	$(env-vars) docker-compose -f docker-compose-pipeline.yml up --build

clean:
	docker volume rm $$(docker volume ls -q) 2>/dev/null; true
	docker system prune --all -f

########################################################################################################################
# Base Commands

dev-down:
	docker-compose down

dev-up:
	$(env-vars) docker-compose up --build

pipeline-down:
	docker-compose -f docker-compose-pipeline.yml down


########################################################################################################################
#These run inside the container

cron-log:
	tail -f /var/log/cron.log

show-cron_tasks:
	tail -f cron_tasks

exec-pipeline:
	docker exec -it `docker ps -q --filter name=nanohub_pipeline` bash

run-tasks:
	docker exec -it `docker ps -q --filter name=nanohub_pipeline` make -f tasks.mk execute


########################################################################################################################
# Others

gcloud_ip=$(shell curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip)

gsetup: setup
	$(shell sed -i -e "/JUPYTER_DISPLAY_IP_ADDRESS/ a JUPYTER_DISPLAY_IP_ADDRESS='$(gcloud_ip)'" .env)

gcloud:
	git pull
	docker-compose down
	$(env-vars) docker-compose up --build