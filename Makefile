

env-vars=UBUNTU_VERSION=$$(cat .env | grep UBUNTU_VERSION= | cut -d '=' -f2) NB_USER=$$(whoami) NB_UID=$$(id -u) NB_GID=$$(id -g) CPUS=$$(getconf _NPROCESSORS_ONLN)

log-level=INFO

IMAGE_ID=`docker images -q nanohub-analytics_remote`

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir_name := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
root_path := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
cwd  := $(shell pwd)

nohup_path=$(root_path)/.output/nohup.out

dev_name=nanohub-analytics_dev
pipeline_name=nanohub_pipeline
########################################################################################################################
#These run on the host

setup:
	cp nanoHUB/.env.dev nanoHUB/.env

git-pull:
	git pull origin `git rev-parse --abbrev-ref HEAD`

dev: git-pull dev-down dev-up

cartopy: git-pull cartopy-down cartopy-up


pipeline: git-pull pipeline-down pipeline-up

pipeline-nohup: nohup pipeline setup-cron-jobs
	tail -f $(nohup_path)

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
	$(env-vars) docker-compose -f docker-compose-pipeline.yml up --build


########################################################################################################################
#These run inside the container

cron-log:
	tail -f /var/log/cron.log

show-cron_tasks:
	tail -f cron_tasks

setup-cron-jobs:
	crontab $(root_path)/cron_pipeline_tasks
	crontab -l

exec-dev:
	docker exec -it `docker ps -q --filter name=$(dev_name)` bash

exec-remote:
	docker exec -it `docker ps -q --filter name=nanohub-analytics_remote` bash

exec-pipeline:
	docker exec -it `docker ps -q --filter name=$(pipeline_name)` bash

run-tasks:
	docker exec `docker ps -q --filter name=$(pipeline_name)` make -f tasks.mk execute

debug-tasks:
	docker exec `docker ps -q --filter name=$(pipeline_name)` make -f tasks.mk execute log-level=DEBUG

run_command:
	docker exec `docker ps -q --filter name=$(pipeline_name)` $(command)

run-clustering:
	docker exec `docker ps -q --filter name=$(pipeline_name)` make -j10 -C nanoHUB/clustering task=xufeng no_save_output=True scratch_dir=/var/tmp
	docker exec `docker ps -q --filter name=$(pipeline_name)` make -j10 -C nanoHUB/clustering task=mike no_save_output=True scratch_dir=/var/tmp
	docker exec `docker ps -q --filter name=$(pipeline_name)` make -j10 -f nanoHUB/clustering/overlap.mk

dev-clustering:
	docker exec `docker ps -q --filter name=$(dev_name)` make -j$(getconf _NPROCESSORS_ONLN) -C nanoHUB/clustering task=xufeng scratch_dir=/var/tmp
	docker exec `docker ps -q --filter name=$(dev_name)` make -j$(getconf _NPROCESSORS_ONLN) -C nanoHUB/clustering task=mike scratch_dir=/var/tmp
	docker exec `docker ps -q --filter name=$(dev_name)` make -j$(getconf _NPROCESSORS_ONLN) -f nanoHUB/clustering/overlap.mk
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

delete-deployment:
	-kubectl delete  -f nanoHUB/ops/kubernetes/builds/${deployment_name}.yaml


replicas=1
revision_history=1
storage=100Gi
geddes-dev: delete-deployment
	-#make remote
	docker commit `docker ps -q --filter name=nanohub-analytics_remote` nanohub-analytics_remote:${image_version}
	docker login geddes-registry.rcac.purdue.edu
	docker tag `docker images -q nanohub-analytics_remote:${image_version}` geddes-registry.rcac.purdue.edu/nanohub/nanohub-analytics:${image_version}
	docker push geddes-registry.rcac.purdue.edu/nanohub/nanohub-analytics:${image_version}
	sed ' \
    		s/{{IMAGE_VERSION}}/${image_version}/g ; \
    		s/{{DEPLOYMENT_NAME}}/${deployment_name}/g ; \
    		s/{{REPLICAS}}/${replicas}/g ; \
    		s/{{REVISION_HISTORY}}/${revision_history}/g ; \
    		s/{{STORAGE}}/${storage}/g ; \
    	' \
    	nanoHUB/ops/kubernetes/kube-file.yaml > nanoHUB/ops/kubernetes/builds/${deployment_name}.yaml
	kubectl apply -f nanoHUB/ops/kubernetes/builds/${deployment_name}.yaml
	git add nanoHUB/ops/kubernetes/builds/${deployment_name}.yaml
	git commit -m "kubernetes deployment build for ${deployment_name}"
	git push origin production

geddes-%:
	sed ' \
		s/{{IMAGE_VERSION}}/$*-${image_version}/g ; \
		s/{{DEPLOYMENT_NAME}}/$*/g ; \
		s/{{REPLICAS}}/${replicas}/g ; \
		s/{{REVISION_HISTORY}}/${revision_history}/g ; \
		s/{{STORAGE}}/${storage}/g ; \
		' \
		nanoHUB/ops/kubernetes/kube-file.yaml > nanoHUB/ops/kubernetes/builds/$*.yaml
	docker commit `docker ps -q --filter name=nanohub-analytics_$*` nanohub-analytics_pipeline:$*-${image_version}
	docker login geddes-registry.rcac.purdue.edu
	docker tag `docker images -q nanohub-analytics_remote:$*-${image_version}` geddes-registry.rcac.purdue.edu/nanohub/nanohub-analytics:$*-${image_version}
	docker push geddes-registry.rcac.purdue.edu/nanohub/nanohub-analytics:$*-${image_version}
	kubectl apply -f nanoHUB/ops/kubernetes/builds/$*.yaml
	git add nanoHUB/ops/kubernetes/builds/$*.yaml
	git commit -m "kubernetes deployment build for $*"
	git push origin production
#EXAMPLE -> docker tag 754acba40643 geddes-registry.rcac.purdue.edu/nanohub/nanohub-analytics:0.4
########################################################################################################################
########################################################################################################################

jupyter-config:
	@sed -n -e '/^c./p' ~/.jupyter/jupyter_notebook_config.py

nohup:
	touch $(nohup_path)