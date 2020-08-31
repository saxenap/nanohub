# nanoHUB analytics and Saleforce CRM integration

## Components
This section contains major components needed for this integration

From Salesforce side,
- Salesforce REST API, especially BULK API 2.0. Entire integration is APEX-free
- Salesforce SOQL for SQL-like data querying from Salesforce
- Salesforce Salescloud CRM admin. access

From nanoHUB DB2 side,
- SQL database on DB2. Read access to databases: nanohub, nanohub_metrics. Read+Write access to wang159_myrmekes
- Airflow for DAG cron job management
- Papermill for Jupyter notebook parameterization and deployment

## Key things to consider before modifying integration
#### DB2 environment and limitation
DB2.nanohub.org has 4 cores and 18 GB memory. It mainly serves as a database backup and light-weight analytics platform. Be mindful about CPU and memory usage. When running code in Airflow, keep the resource allocation to single core.

Balance what can be done in SQL and Python. Complex and inefficient operations in SQL can potentially lock many of the other processes going on with the database, i.e. scheduled backups. Bring tables into Python for joins/aggregations if needed and watch out for locks.

The organization table containing information of 7 Million companies occupies significant memory. Be mindful and creative to avoid excessive memory use. 

#### Salesforce API limits
The integration heavily utilizes Bulk API 2.0 for bulk upserts/requests/deletions. Each bulk API can contain unto 32000 characters and counts as 1 API call. If too large, the data must be divided into chucks and transferred in several bulk API calls. A utility object DB2SalesforceAPI is written to handle this automatically and other REST API calls to Salesforce. 

Keep in mind that Bulk API calls are asynchronous when implementing new features or re-arranging current workflows.

See (https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm) for detailed API limits. 

## Overview

The overall integration involves the calculation and transfer of various data pieces (user information, tool information, clusters detected from ML model, etc.) from DB2 to Salesforce. Each individual task follows roughly the same format:

1. Obtain data from SQL database
2. Obtain data from Salesforce if needed
3. Calculations
4. Send data to Salesforce

Each individual task is a Jupiter notebook and can be run independently from each other. The following tasks are available:
|Notebook name|Description|
|-------------------------------------------|-------------------------------------------------------------|
|task_citations.ipynb|Update nanoHUB citations|
|task_citations_map_contacts.ipynb|Associate citation -> authors who are existing users|
|task_citations_map_leads.ipynb|Associate citation -> authors who are not nanoHUB users|
|task_issue_url.ipynb|Update URL issues|
|task_tool_basic_updates.ipynb|Update tool information|
|task_tools_map_authors.ipynb|Associate tool -> author|
|task_tools_map_contacts.ipynb|Associate tool -> tool users|
|task_tool_usage_clusters.ipynb|Update tool usage clusters|
|task_determine_contact_cluster_org.ipynb|Associate clusters -> organization|
|task_organization.ipynb|Update organization| Let me update institution information - see organization object in sf
|task_orgs_map_contacts.ipynb|Determine most likely organization for each contact|
|task_tool_usage_clusters_map_contacts.ipynb|Associate clusters -> users|
|task_tool_usage_clusters_map_tools.ipynb|Associate clusters -> tools|
|task_user_basic_updates.ipynb|Update user information|

In addition, a utility for mass Salesforce record deletion is available:
utility_delete_all_records.ipynb


Airflow is used to construct workflows from these individual tasks and schedule them for run.
