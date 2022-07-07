

env-vars=UBUNTU_VERSION=$$(cat .env | grep UBUNTU_VERSION= | cut -d '=' -f2) NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g) CPUS=$$(getconf _NPROCESSORS_ONLN)

log-level=INFO

IMAGE_ID=`docker images -q nanohub-analytics_remote`
########################################################################################################################
#These run on the host

setup:
	cp nanoHUB/.env.dev nanoHUB/.env

git-pull:
	git pull origin `git rev-parse --abbrev-ref HEAD`

dev: git-pull dev-down dev-up

cartopy: git-pull cartopy-down cartopy-up

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
pipeline: git-pull pipeline-down pipeline-up
	tail -f nohup.out
=======
pipeline: nohup git-pull pipeline-down pipeline-up setup-cron-jobs
=======
pipeline: nohup git-pull pipeline-down pipeline-up
>>>>>>> parent of cce7d58 (change nohup path)
	tail -f $(nohup_path)
>>>>>>> parent of 4ef83d7 (change nohup path)
=======
pipeline: git-pull pipeline-down pipeline-up
	tail -f nohup.out
>>>>>>> parent of 7b85d9d (change nohup path)

remote: git-pull remote-down remote-up

clean:
	docker volume rm $$(docker volume ls -q) 2>/dev/null; true
	docker system prune --all -f

########################################################################################################################
# Base Commands

dev-down:
	$(env-vars) docker-compose down

dev-up:
	$(env-vars) docker-compose up --build

remote-down:
	$(env-vars) docker-compose -f docker-compose-remote.yml down

remote-up:
	$(env-vars) docker-compose -f docker-compose-remote.yml up --build

cartopy-down:
	$(env-vars) docker-compose -f docker-compose-cartopy.yml down

cartopy-up:
	$(env-vars) docker-compose -f docker-compose-cartopy.yml up --build

pipeline-down:
	$(env-vars) docker-compose -f docker-compose-pipeline.yml down

pipeline-up:
	$(env-vars) nohup docker-compose -f docker-compose-pipeline.yml up --build </dev/null >nohup.out 2>&1 &


########################################################################################################################
#These run inside the container

cron-log:
	tail -f /var/log/cron.log

show-cron_tasks:
	tail -f cron_tasks

setup-cron-jobs:
	crontab ~/cron_pipeline_tasks
	cat ~/cron_pipeline_tasks

exec-dev:
	docker exec -it `docker ps -q --filter name=nanohub-analytics_dev` bash

exec-remote:
	docker exec -it `docker ps -q --filter name=nanohub-analytics_remote` bash

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


########################################################################################################################
########################################################################################################################

pipenv-update:
	$(MAKE) _pipenv-update || $(MAKE) error_pipenv-update

error_pipenv-update: _pipenv-update

_pipenv-update:
	pipenv install -e .
	pipenv lock -r --dev > requirements.txt

########################################################################################################################
########################################################################################################################

geddes-image:
	docker commit `docker ps -q --filter name=nanohub-analytics_remote` nanohub-analytics_remote:${version}
	docker login geddes-registry.rcac.purdue.edu
	docker tag `docker images -q nanohub-analytics_remote:${version}` geddes-registry.rcac.purdue.edu/nanohub/nanohub-analytics:${version}
	docker push geddes-registry.rcac.purdue.edu/nanohub/nanohub-analytics:${version}
#EXAMPLE -> docker tag 754acba40643 geddes-registry.rcac.purdue.edu/nanohub/nanohub-analytics:0.4
########################################################################################################################
########################################################################################################################

jupyter-config:
	@sed -n -e '/^c./p' ~/.jupyter/jupyter_notebook_config.py