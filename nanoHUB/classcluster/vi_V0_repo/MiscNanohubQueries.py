def getNonExperimentalCitedUsers(connection):
	sql = """
		select distinct jxp.username from jos_citations as jc1, jos_citations_authors as jca, jos_xprofiles as jxp
		where jca.cid = jc.id and jca.author_uid <> 0 and exp_list_exp_data = 1 and published = 1 and jca.author_uid = jxp.uidNumber and jca.author_uid not in 
		(select distinct jca.author_uid from jos_citations as jc, jos_citations_authors as jca where jca.cid = jc.id and jca.author_uid <> 0 and exp_data = 1 and published = 1);
