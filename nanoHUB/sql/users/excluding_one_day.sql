SELECT id, name, registerDate, lastvisitDate, email, usertype, block, approved
FROM jos_users
WHERE registerDate <= DATE_SUB(lastvisitDate, INTERVAL 1 DAY)