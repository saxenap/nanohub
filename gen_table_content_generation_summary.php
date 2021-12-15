<?php

# This script generates the table: "Table3.9 - Content Generation Summary"
# Usage: php gen_table_content_generation_summary.php > out_content_generation_summary
# This script generates a csv file which needs to be formatted into the final table: http://vox.hubzero.org/report/ncnreport/2013
# Set parameters between 'TODO-Begin' and 'TODO-End'
# ---------------------------------------------------------------------------------------------------------

require_once('/var/www/tmp/metrics_ncnreport/hub_parameters.php');
require_once('/opt/hubzero/bin/metrics/includes/db_connect.php');
require_once('/opt/hubzero/bin/metrics/includes/func_misc.php');

$db_hub = db_connect('db_hub');

$cumulative = 1;

# ---------------------------------------------------------------------------------------------------------
# TODO-Begin

## List of Resource Types used in this report
// Tools: 7
// Learning Modules: 4
// Online Presentations: 1
// Courses: 6 
// Workshops: 2
// Animations: 5
// Publications: 3
// Downloads: 9
// Notes: 10
// Teaching Materials: 39
// Non-Interative Educational Material: ?
// Non Interactive documents: ?
$res_types = array(7,4,1,6,2,5,3,9,10,39);

## List of Tags used in this report
// Tutorials: 25
// Research Seminars: 27
// Serial Tools: 226
// Parallel Tools: 227
$res_tags = array(226,227,25,27);

# TODO-End
# ---------------------------------------------------------------------------------------------------------

print "\n,Pre-NCN,Year 1,Year 2,Year 3,Year 4,Year 5,Year 6,Year 7,Year 8, Year 9, Year 10, Year 11, Year 12, Year 13, Year 14, Year 15, Year 16, Year 17, Year 18, Last 12 Months, Year 19 (partial), Cummulative\n";
foreach($res_types as $type) {

	$sql = 'SELECT type FROM nanohub.jos_resource_types where id='.$type;
	$result = mysql_query($sql, $db_hub);
	if($result) {
		if(mysql_num_rows($result) > 0) {
   			while($row = mysql_fetch_row($result)) {
   		   	 	$res_type=$row[0];
			}
		}
	} else {
		echo mysql_error($db_hub)." while executing ".$sql."\n";
	    die;
	}

	print "\n".$res_type."\n";
	# Special Case used in 2007 report
	// remove published=1 for punch tools
	/*
	if ($type == 7) {
		$published = " AND res.published < 2 ";
	} else {
		$published = " AND res.published=1 ";
	}*/
	$published = " AND res.published=1 ";

	# Total
	$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res WHERE res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1 AND res.type="'.$type.'" ';
	compute_years($db_hub, "Total", $statement,1);
	print "\n";

	# NCN Purdue 
	$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid AND res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1 AND objtags.tbl="resources" AND res.type="'.$type.'" ';
	compute_years($db_hub, "NCN Purdue", $statement);
	print "\n";

	/*
	# NCN Other
	$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid '.$published.' AND res.access!=1 AND res.access!=4 AND res.standalone=1 AND objtags.tbl="resources" AND res.type="'.$type.'" ';
	compute_years($db_hub, "NCN Other", $statement);
	print "\n";
	*/

	# Outside NCN
	$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid AND res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1 AND objtags.tbl="resources" AND res.type="'.$type.'" ';
	compute_years($db_hub, "Outside NCN", $statement);
	print "\n";

}


// -------
// All "and more" Resources 
print "\nTotal 'and more' Content\n";

# Special Case used in 2007 report
#$published = " AND res.published < 2 ";
$published = " AND res.published = 1 ";

# Total
$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res WHERE res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1 AND res.type <> 7';
compute_years($db_hub, "Total", $statement,1);
print "\n";

# NCN Purdue
$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid AND res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1 AND objtags.tbl="resources" AND res.type <> 7 ';
compute_years($db_hub, "NCN Purdue", $statement);
print "\n";

/*
# NCN Other
$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid '.$published.' AND res.access!=1 AND res.access!=4 AND res.standalone=1 AND objtags.tbl="resources" AND res.type <> 7';
compute_years($db_hub, "NCN Other", $statement);
print "\n";
*/

# Outside NCN
$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid AND res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1 AND objtags.tbl="resources" AND res.type <> 7';
compute_years($db_hub, "Outside NCN", $statement);
print "\n\n";

// -------
// All Resources 
print "Total Resources\n";

#$published = " AND res.published < 2 ";
$published = " AND res.published = 1 ";

# Total
$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res WHERE res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1';
compute_years($db_hub, "Total", $statement,1);
print "\n";

# NCN Purdue
$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid AND res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1 AND objtags.tbl="resources" ';
compute_years($db_hub, "NCN Purdue", $statement);
print "\n";

/*
# NCN Other
$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid '.$published.' AND res.access!=1 AND res.access!=4 AND res.standalone=1 AND objtags.tbl="resources" ';
compute_years($db_hub, "NCN Other", $statement);
print "\n";
*/

# Outside NCN
$statement = 'SELECT COUNT(DISTINCT(res.id)) FROM nanohub.jos_resources AS res, nanohub.jos_tags_object AS objtags WHERE res.id=objtags.objectid AND res.access!=1 AND res.access!=4 '.$published.' AND res.standalone=1 AND objtags.tbl="resources" ';
compute_years($db_hub, "Outside NCN", $statement);
print "\n\n";

db_close($db_hub);
// -------

function compute_years($db_hub, $label, $statement, $total=0){

	global $cumulative, $report_db;

	print $label.",";
	$sql = 'SELECT period, startdate, enddate FROM '.$report_db.'.report_periods order by enddate ASC';
	print "sql: ".$sql;
	$result = mysql_query($sql, $db_hub);
	if($result) {
		if(mysql_num_rows($result) > 0) {
   			while($row = mysql_fetch_row($result)) {
				$period = $row[0];
				$startdate = $row[1];
				if ($cumulative)
					$startdate = '2000-01-01';
				$enddate = $row[2];
				if (!$total) {
					$tags = '';
					$tags = get_ncn_participation($db_hub, $period, $label);
					$sql_ = $statement.' AND res.publish_up > "'.$startdate.'" AND res.publish_up < "'.$enddate.'" AND objtags.tagid IN ('.$tags.')';
				} else {
					$sql_ = $statement.' AND res.publish_up > "'.$startdate.'" AND res.publish_up < "'.$enddate.'"';
				}
				$result_ = mysql_query($sql_, $db_hub);
				if($result_) {
					if(mysql_num_rows($result_) > 0) {
   						while($row_ = mysql_fetch_row($result_)) {
							$items = $row_[0];
						}
					}
				} else {
					echo mysql_error($db_hub)." while executing ".$sql_."\n";
	    			die;
				}
				if ($items) {
					print $items.",";
				} else {
					print ",";
				}
			}
		}
	} else {
		echo mysql_error($db_hub)." while executing ".$sql."\n";
	    die;
	}
}

function get_ncn_participation ($db_hub, $period, $label) {

	global $report_db;

	$tag_list = '';
	if ($label == "NCN Purdue") {
		$sql = 'SELECT tagid FROM '.$report_db.'.report_ncn_tags WHERE report_tag IN (SELECT report_tag FROM '.$report_db.'.report_ncn_participation WHERE inside = 1 AND report_tag = "ncn_purdue" AND period = "'.$period.'")';
	} else if ($label == "NCN Other") {
		$sql = 'SELECT tagid FROM '.$report_db.'.report_ncn_tags WHERE report_tag IN (SELECT report_tag FROM '.$report_db.'.report_ncn_participation WHERE inside = 1 AND report_tag <> "ncn_purdue" AND period = "'.$period.'")';
	} else if ($label == "Outside NCN") {
	//	$sql = 'SELECT tagid FROM '.$report_db.'.report_ncn_tags WHERE report_tag IN (SELECT report_tag FROM '.$report_db.'.report_ncn_participation WHERE report_tag <> "ncn_purdue" AND period = "'.$period.'")';
		$sql = 'SELECT tagid FROM '.$report_db.'.report_ncn_tags WHERE report_tag IN (SELECT report_tag FROM '.$report_db.'.report_ncn_participation WHERE report_tag = "ncn_outside" AND period = "'.$period.'")';
	} else {
		return;
	}
	$result = mysql_query($sql, $db_hub);
	if($result) {
		if(mysql_num_rows($result) > 0) {
   			while($row = mysql_fetch_row($result)) {
				$tag_list .= $row[0].',';
			}
		}
	} else {
		echo mysql_error($db_hub)." while executing ".$sql."\n";
	    die;
	}
	$tag_list = rtrim($tag_list, ',');

	return $tag_list;
}
?>

