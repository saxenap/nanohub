SELECT
FROM jos_users
WHERE registerDate > DATE_SUB(lastvisitDate, INTERVAL 1 DAY)
;