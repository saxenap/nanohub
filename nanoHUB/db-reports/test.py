from nanoHUB.application import Application
application = Application.get_instance()
nanohub_db = application.new_db_engine('nanohub')
sql_query = 'select id, uid, author from jos_citations'
jos_citations = pd.read_sql_query(sql_query, nanohub_db)
print(jos_citations.head(20))
