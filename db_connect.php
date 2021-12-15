<?php
error_reporting(E_ALL & ~E_NOTICE & ~E_DEPRECATED);

function db_connect($dblink) {

	switch($dblink) {

		case 'db_hub':
			$db = mysql_connect($GLOBALS['db_host'], $GLOBALS['db_user'], $GLOBALS['db_pass'], true);
			mysql_select_db($GLOBALS['hub_db'], $db);
			break;

		case 'db_net':
			$db = mysql_connect('localhost', $GLOBALS['db_net_user'], $GLOBALS['db_net_pass'], true);
			mysql_select_db($GLOBALS['net_db'], $db);
			break;

		default:
			print 'Unrecognized database link '.$dblink.n;
    		die;
	}
	
	return $db;

}

function db_close($db) {

	mysql_close($db);

}

?>
