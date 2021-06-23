PHONY: execute-notebook git-push
DOCKER = $(shell which docker)

execute-notebook:
	$(DOCKER) run --env-file /app/.envvars -a STDOUT --rm --name $(name)-$(shell date +'%F-%s') pipeline_tasks make execute-notebook name=$(name)