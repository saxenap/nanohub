#this gets gerhard's tools
SELECT distinct TV.toolname FROM jos_tool_version AS TV, jos_tool_authors AS TA WHERE TV. id = TA.version_id AND TA.uid = 3482;
