create table ANALYTICS_derived_data.simulations
(
  id              int unsigned auto_increment,
  username        varchar(100)      not null,
  user_id         int      unsigned not null,
  tool_count      int      unsigned not null,
  session_count   int      unsigned not null,
  sim_count       int      unsigned not null,
  earliest_sim    datetime          not null,
  latest_sim      datetime          not null,
  active_duration int      unsigned not null,
  PRIMARY KEY (`id`)
)
  ENGINE=InnoDB DEFAULT CHARSET=utf8
;


SELECT DISTINCT rollup.user AS username,
                rollup.user_id AS user_id,
                COUNT(rollup.tool_name) AS tool_count,
                COUNT(DISTINCT starts.id) AS session_count,
                SUM(rollup.tool_sim_count) AS sim_count,
                MIN(rollup.earliest_sim) AS earliest_sim,
                MAX(rollup.latest_sim) AS latest_sim,
                DATEDIFF(rollup.lastvisitDate, rollup.registerDate) AS active_duration,
                DATEDIFF(MAX(rollup.latest_sim), MIN(rollup.earliest_sim)) AS sim_lifetime,
                MAX(rollup.max_entryId) AS last_entryId,
                rollup.*
FROM (SELECT events.user        AS user,
             MIN(events.start)  AS earliest_sim,
             MAX(events.start)  AS latest_sim,
             versions.toolname  AS tool_name,
             COUNT(DISTINCT events.entryID)           AS tool_sim_count,
             MAX(events.entryID) AS max_entryId,
             users.id           AS user_id,
             users.registerDate AS registerDate,
             users.lastvisitDate AS lastvisitDate
      FROM nanohub_metrics.toolevents events
        INNER JOIN nanohub.jos_tool_version versions
      ON versions.instance = events.tool
        INNER JOIN nanohub.jos_users users
        ON users.username = events.user
      WHERE events.user != ''
        AND events.user IN('asep.ridwans', 'chirag_garg')
        #         AND events.entryId >= 201661640
      GROUP BY events.user, versions.toolname
     ) AS rollup
       INNER JOIN nanohub_metrics.toolstart starts
                  ON starts.user = rollup.user
GROUP BY rollup.user
;

SELECT MAX(events.entryID) AS max_entryId
FROM nanohub_metrics.toolevents events;



SELECT *
FROM nanohub_metrics.toolevents
WHERE entryID = 201662655;


TRUNCATE ANALYTICS_derived_data.simulations;
INSERT INTO ANALYTICS_derived_data.simulations
(username,
 user_id,
 tool_count,
 session_count,
 sim_count,
 earliest_sim,
 latest_sim,
 active_duration,
 sim_lifetime,
 last_entryId)
SELECT DISTINCT rollup.user AS username,
                rollup.user_id AS user_id,
                COUNT(DISTINCT rollup.tool_name) AS tool_count,
                (SELECT COUNT(*) FROM nanohub_metrics.toolstart WHERE user = rollup.user) AS session_count,
                (SELECT COUNT(*) FROM nanohub_metrics.toolevents WHERE user = rollup.user) AS sim_count,
                MIN(rollup.earliest_sim) AS earliest_sim,
                MAX(rollup.latest_sim) AS latest_sim,
                DATEDIFF(rollup.lastvisitDate, rollup.registerDate) AS active_duration,
                DATEDIFF(MAX(rollup.latest_sim), MIN(rollup.earliest_sim)) AS sim_lifetime,
                MAX(rollup.max_entryId) AS last_entryId
FROM (SELECT DISTINCT events.user        AS user,
                      MIN(events.start)  AS earliest_sim,
                      MAX(events.start)  AS latest_sim,
                      COUNT(*)  AS tool_name,
                      COUNT(DISTINCT events.entryID) AS tool_sim_count,
#             COUNT(DISTINCT starts.id) AS tool_session_count,
                      MAX(events.entryID) AS max_entryId,
                      users.id           AS user_id,
                      users.registerDate AS registerDate,
                      users.lastvisitDate AS lastvisitDate
      FROM nanohub_metrics.toolevents events
        INNER JOIN nanohub.jos_tool_version versions
      ON versions.instance = events.tool
        INNER JOIN nanohub.jos_users users
        ON users.username = events.user
      WHERE events.user != ''
      GROUP BY events.user, versions.toolname
     ) AS rollup
WHERE  rollup.user != ''
  AND rollup.user IN (SELECT username FROM nanohub.jos_users WHERE registerDate >= '2022-10-10 16:31:54.0')
GROUP BY rollup.user
;
SELECT * FROM ANALYTICS_derived_data.simulations;

SELECT username, registerDate FROM nanohub.jos_users WHERE registerDate > '2022-10-10 00:00:00';
SELECT DISTINCT rollup.user AS username,
                rollup.user_id AS user_id,
                COUNT(DISTINCT rollup.tool_name) AS tool_count,
                (SELECT COUNT(*) FROM nanohub_metrics.toolstart WHERE user = rollup.user) AS session_count,
                (SELECT COUNT(*) FROM nanohub_metrics.toolevents WHERE user = rollup.user) AS sim_count,
                MIN(rollup.earliest_sim) AS earliest_sim,
                MAX(rollup.latest_sim) AS latest_sim,
                DATEDIFF(rollup.lastvisitDate, rollup.registerDate) AS active_duration,
                DATEDIFF(MAX(rollup.latest_sim), MIN(rollup.earliest_sim)) AS sim_lifetime,
                MAX(rollup.max_entryId) AS last_entryId,
                rollup.*
FROM (SELECT DISTINCT events.user        AS user,
             MIN(events.start)  AS earliest_sim,
             MAX(events.start)  AS latest_sim,
             COUNT(*)  AS tool_name,
             COUNT(DISTINCT events.entryID) AS tool_sim_count,
#             COUNT(DISTINCT starts.id) AS tool_session_count,
             MAX(events.entryID) AS max_entryId,
             users.id           AS user_id,
             users.registerDate AS registerDate,
             users.lastvisitDate AS lastvisitDate
      FROM nanohub_metrics.toolevents events
        INNER JOIN nanohub.jos_tool_version versions
      ON versions.instance = events.tool
        INNER JOIN nanohub.jos_users users
        ON users.username = events.user
      WHERE events.user != ''
        AND events.user IN ('asep.ridwans', 'chirag_garg')
      GROUP BY events.user, versions.toolname
     ) AS rollup
WHERE  rollup.user != ''
  AND rollup.max_entryId
GROUP BY rollup.user;

SELECT events.user        AS user,
       MIN(events.start)  AS earliest_sim,
       MAX(events.start)  AS latest_sim,
       versions.toolname  AS tool_name,
       COUNT(DISTINCT events.entryID) AS tool_sim_count,
       MAX(events.entryID) AS max_entryId,
       users.id           AS user_id,
       users.registerDate AS registerDate,
       users.lastvisitDate AS lastvisitDate
FROM nanohub_metrics.toolevents events
  INNER JOIN nanohub.jos_tool_version versions
ON versions.instance = events.tool
  INNER JOIN nanohub.jos_users users
  ON users.username = events.user
WHERE events.user != ''
  AND events.user IN ('asep.ridwans', 'chirag_garg')
GROUP BY events.user, versions.toolname

SELECT
  events.user AS user,
  events.entryID,
  versions.toolname
FROM nanohub_metrics.toolevents events
  INNER JOIN nanohub.jos_tool_version versions
ON versions.instance = events.tool
WHERE
  events.user != ''
  AND events.user = 'asep.ridwans'
GROUP BY events.user, versions.toolname


SELECT COUNT(*)
FROM nanohub_metrics.toolstart
WHERE user = 'asep.ridwans'

SELECT COUNT(DISTINCT entryID)
FROM nanohub_metrics.toolevents
WHERE user = 'asep.ridwans'