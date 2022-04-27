

env-vars=UBUNTU_VERSION=$$(cat .env | grep UBUNTU_VERSION= | cut -d '=' -f2) NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g) CPUS=$$(getconf _NPROCESSORS_ONLN)

log-level=INFO
########################################################################################################################
#These run on the host

setup:
	cp nanoHUB/.env.dev nanoHUB/.env

dev:
	git pull origin `git rev-parse --abbrev-ref HEAD`
	make dev-down
	make dev-up

cartopy:
	git pull origin `git rev-parse --abbrev-ref HEAD`
	make cartopy-down
	make cartopy-up

pipeline:
	git pull origin `git rev-parse --abbrev-ref HEAD`
	make pipeline-down
	$(env-vars) docker-compose -f docker-compose-pipeline.yml up --build

clean:
	docker volume rm $$(docker volume ls -q) 2>/dev/null; true
	docker system prune --all -f

########################################################################################################################
# Base Commands

dev-down:
	$(env-vars) docker-compose down

dev-up:
	$(env-vars) docker-compose up --build

cartopy-down:
	$(env-vars) docker-compose -f docker-compose-cartopy.yml down

cartopy-up:
	$(env-vars) docker-compose -f docker-compose-cartopy.yml up --build

pipeline-down:
	$(env-vars) docker-compose -f docker-compose-pipeline.yml down


########################################################################################################################
#These run inside the container

cron-log:
	tail -f /var/log/cron.log

show-cron_tasks:
	tail -f cron_tasks


exec-dev:
	docker exec -it `docker ps -q --filter name=nanohub-analytics_dev` bash

exec-pipeline:
	docker exec -it `docker ps -q --filter name=nanohub_pipeline` bash

run-tasks:
	docker exec `docker ps -q --filter name=nanohub_pipeline` make -f tasks.mk execute

debug-tasks:
	docker exec `docker ps -q --filter name=nanohub_pipeline` make -f tasks.mk execute log-level=DEBUG

run_command:
	docker exec `docker ps -q --filter name=nanohub_pipeline` $(command)

run-clustering:
	docker exec `docker ps -q --filter name=nanohub_dev` make -C -j$(getconf _NPROCESSORS_ONLN) nanoHUB/clustering
########################################################################################################################
# Others

gcloud_ip=$(shell curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip)

gsetup: setup
	$(shell sed -i -e "/JUPYTER_DISPLAY_IP_ADDRESS/ a JUPYTER_DISPLAY_IP_ADDRESS='$(gcloud_ip)'" .env)

gcloud:
	git pull
	docker-compose down
	$(env-vars) docker-compose up --build
