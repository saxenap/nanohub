#!make
env_vars:
	env

test:
	nanoHUB task execute \
		nanoHUB/pipeline/salesforce/_task_test.ipynb \
	--log-level=INFO 2>&1 | /usr/bin/logger -t PIPELINE

execute:
	nanoHUB task execute \
		nanoHUB/pipeline/salesforce/_task_test.ipynb  \
		nanoHUB/pipeline/salesforce/task_citations.ipynb  \
		nanoHUB/pipeline/salesforce/task_citations_map_contacts.ipynb  \
		nanoHUB/pipeline/salesforce/task_citations_map_leads.ipynb   \
		nanoHUB/pipeline/salesforce/task_determine_contact_cluster_org.ipynb  \
		nanoHUB/pipeline/salesforce/task_issue_url.ipynb  \
		nanoHUB/pipeline/salesforce/task_organization.ipynb  \
		nanoHUB/pipeline/salesforce/task_orgs_map_contacts.ipynb  \
		nanoHUB/pipeline/salesforce/task_tool_basic_updates.ipynb  \
		nanoHUB/pipeline/salesforce/task_tools_map_authors.ipynb   \
		nanoHUB/pipeline/salesforce/task_tools_map_contacts.ipynb  \
		nanoHUB/pipeline/salesforce/task_user_basic_updates.ipynb  \
		nanoHUB/pipeline/salesforce/delete_spam_users.ipynb  \
		nanoHUB/pipeline/salesforce/task_update_email_preferences.ipynb  \
		nanoHUB/pipeline/salesforce/task_nh_survey_urls.ipynb  \
		nanoHUB/pipeline/salesforce/task_user_org_reclass.ipynb  \
		nanoHUB/pipeline/salesforce/task_update_static_personalinfo.ipynb  \
		nanoHUB/pipeline/salesforce/db2users_remap_sf.ipynb  \
		nanoHUB/pipeline/salesforce/task_nh_usage_survey.ipynb  \
		nanoHUB/pipeline/salesforce/task_user_contribution_update.ipynb  \
		nanoHUB/pipeline/researcher_scraping/main_file.py  \
		nanoHUB/pipeline/SF_dataimports/general_imports.ipynb \
	--log-level=INFO 2>&1 | /usr/bin/logger -t PIPELINE