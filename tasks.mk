#!make
ROOT_DIR=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SALESFORCE_DIR=$(ROOT_DIR)/nanoHUB/pipeline/salesforce

env_vars:
	env

heartbeat:
	/usr/bin/logger -t PIPELINE -p user.info "Heart Beat Check."

test:
	nanoHUB task execute \
		$(SALESFORCE_DIR)/_task_test.ipynb \
	--log-level=INFO 2>&1 | /usr/bin/logger -t PIPELINE

execute:
	nanoHUB task execute \
		$(SALESFORCE_DIR)/_task_test.ipynb  \
		$(SALESFORCE_DIR)/task_citations.ipynb  \
		$(SALESFORCE_DIR)/task_citations_map_contacts.ipynb  \
		$(SALESFORCE_DIR)/task_citations_map_leads.ipynb   \
		$(SALESFORCE_DIR)/task_determine_contact_cluster_org.ipynb  \
		$(SALESFORCE_DIR)/task_issue_url.ipynb  \
		$(SALESFORCE_DIR)/task_organization.ipynb  \
		$(SALESFORCE_DIR)/task_orgs_map_contacts.ipynb  \
		$(SALESFORCE_DIR)/task_tool_basic_updates.ipynb  \
		$(SALESFORCE_DIR)/task_tools_map_authors.ipynb   \
		$(SALESFORCE_DIR)/task_tools_map_contacts.ipynb  \
		$(SALESFORCE_DIR)/task_user_basic_updates.ipynb  \
		$(SALESFORCE_DIR)/delete_spam_users.ipynb  \
		$(SALESFORCE_DIR)/task_update_email_preferences.ipynb  \
		$(SALESFORCE_DIR)/task_nh_survey_urls.ipynb  \
		$(SALESFORCE_DIR)/task_user_org_reclass.ipynb  \
		$(SALESFORCE_DIR)/task_update_static_personalinfo.ipynb  \
		$(SALESFORCE_DIR)/db2users_remap_sf.ipynb  \
		$(SALESFORCE_DIR)/task_nh_usage_survey.ipynb  \
		$(SALESFORCE_DIR)/task_user_contribution_update.ipynb  \
		nanoHUB/pipeline/researcher_scraping/main_file.py  \
		nanoHUB/pipeline/SF_dataimports/general_imports.ipynb \
	--log-level=INFO 2>&1 | /usr/bin/logger -t PIPELINE