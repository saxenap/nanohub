#!make
THIS_FILE := $(lastword $(MAKEFILE_LIST))

ROOT_DIR=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
NANOHUB_DIR=$(ROOT_DIR)/nanoHUB

PIPELINE_DIR=$(NANOHUB_DIR)/pipeline

#CALL_MAIN=python3 $(ROOT_DIR)/nanoHUB/__main__.py
CALL_MAIN=nanohub

EXECUTE_TASK=$(CALL_MAIN) task execute
log-context='pipeline_task'

SALESFORCE_BACKUP=$(CALL_MAIN) backup salesforce
SALESFORCE_DIR=$(PIPELINE_DIR)/salesforce
SF_BACKUP_DOMAIN='backups'
DOMAIN=${SF_BACKUP_DOMAIN}
log-context='SF_Backups'

log-level=INFO
log-level-string="--log-level $(log-level)"

logger=--log-level=$(log-level) 2>&1 | /usr/bin/logger -t ${log-context}

TASKS=$(SALESFORCE_DIR)/_task_test.ipynb \
	$(SALESFORCE_DIR)/task_citations.ipynb  \
	$(SALESFORCE_DIR)/task_citations_map_leads.ipynb   \
	$(SALESFORCE_DIR)/task_issue_url.ipynb  \
	$(SALESFORCE_DIR)/task_organization.ipynb  \
	$(SALESFORCE_DIR)/task_orgs_map_contacts.ipynb  \
	$(SALESFORCE_DIR)/task_tool_basic_updates.ipynb  \
	$(SALESFORCE_DIR)/task_tools_map_authors.ipynb   \
	$(SALESFORCE_DIR)/task_tools_map_contacts.ipynb  \
	$(SALESFORCE_DIR)/task_user_basic_updates-2.ipynb  \
	$(SALESFORCE_DIR)/delete_spam_users.ipynb  \
	$(SALESFORCE_DIR)/task_update_email_preferences.ipynb  \
	$(SALESFORCE_DIR)/task_nh_survey_urls.ipynb  \
	$(SALESFORCE_DIR)/task_user_org_reclass.ipynb  \
	$(SALESFORCE_DIR)/task_update_static_personalinfo.ipynb  \
	$(SALESFORCE_DIR)/db2users_remap_sf.ipynb  \
	$(SALESFORCE_DIR)/task_nh_usage_survey.ipynb  \
	$(SALESFORCE_DIR)/task_nh_groups.ipynb  \
	$(SALESFORCE_DIR)/simulation_user_lifetimes-2.ipynb   \
	$(SALESFORCE_DIR)/task_user_contribution_update.ipynb  \
	$(PIPELINE_DIR)/SF_dataimports/general_imports.ipynb

TASKS_ERRORS=\
	$(PIPELINE_DIR)/researcher_scraping/main_file.py  \
	$(SALESFORCE_DIR)/task_citations_map_contacts.ipynb

.PHONY: task

env_vars:
	env

heartbeat:
	/usr/bin/logger -t heartbeat -p user.info "Heart Beat Check."

execute:
	mkdir -p .output && $(EXECUTE_TASK) $(TASKS) log-context='pipeline_tasks'

test:
	$(MAKE) -f $(THIS_FILE) execute TASKS=$(SALESFORCE_DIR)/_task_test.ipynb log-context='task_test'

salesforce-backup:
	nohup $(SALESFORCE_BACKUP) DOMAIN=$(DOMAIN) log-context='manual_salesforce_backup'
	tail -f nohup.out

pipeline-salesforce-backup:
	$(SALESFORCE_BACKUP) DOMAIN=$(DOMAIN) log-context='salesforce_backup'

import:
	$(MAKE) -f $(THIS_FILE) execute TASKS=$(PIPELINE_DIR)/SF_dataimports/general_imports.ipynb log-context='data_imports'

#$(SALESFORCE_DIR)/task_determine_contact_cluster_org.ipynb  \