<?php

error_reporting(E_ALL & ~E_NOTICE);
@ini_set('display_errors','1');

ini_set('memory_limit', '3G');
date_default_timezone_set("UTC");


define('n', "\n");
define('t', "\t");

// This is a temporary fix to handle the new nanoHUB CMS updates. Please fix the commented part of the code below.
// The variables between "BEGIN TEMP FIX" and "END TEMP FIX" could change and the metrics will break.

// BEGIN TEMP FIX *************

$hub_db = '`nanohub`';
$hub_dir = '/www/nanohub';
$db_host = 'lightsout.nanohub.org';
$db_user = 'nanohub';
$db_pass = 'XXX';
$db_prefix = 'jos_';

$metrics_db = 'nanohub_metrics';
$report_db = 'nanohub_annualreport';
$mw_db = 'narwhal';
$net_db = 'network';

$db_net_host = 'lightsout.nanohub.org';
$db_net_user = 'geodb';
$db_net_pass = 'XXX';
$net_db = 'network';

// END TEMP FIX ***************

/*

$inicontents = file_get_contents('/etc/hubzero.conf');
$inicontents = preg_replace('/\[DEFAULT]/m','[default]', $inicontents);
$inicontents = preg_replace('/^\s*BaseDN\s*=\s*(.*)$/m','BaseDN="$1"', $inicontents);
$inicontents = preg_replace('/^\s*Org\s*=\s*(.*)$/m','Org="$1"', $inicontents);
$result = parse_ini_string($inicontents, true);

if (!is_array($result))
{
    print date('Y-m-d H:is:s T').' '.$_SERVER['argv'][0].': '.'Hubzero Configuration file /etc/hubzero.conf missing or invalid'.n;
    die;
}

if (is_array($result['default']))
    $DocumentRoot = $result[$result['default']['site']]['DocumentRoot'];
else if (is_array($result[key($result)]))
    $DocumentRoot = $result[key($result)]['DocumentRoot'];
else
    $DocumentRoot = $result['DocumentRoot'];

define( '_JEXEC', 1 );
define('JPATH_BASE', $DocumentRoot);
define( 'DS', DIRECTORY_SEPARATOR );

require_once ( JPATH_BASE .DS.'includes'.DS.'defines.php' );
require_once ( JPATH_BASE .DS.'includes'.DS.'framework.php' );

$mainframe = JFactory::getApplication('site');
$mainframe->initialise();

$jconfig    = JFactory::getConfig();

$hub_db = $jconfig->getValue('config.db');
$hub_dir = JPATH_BASE;
$db_host = $jconfig->getValue('config.host');
$db_user = $jconfig->getValue('config.user');
$db_pass = $jconfig->getValue('config.password');
$db_prefix = $jconfig->getValue('config.dbprefix');

$metrics_db = '`'.$hub_db.'_metrics`';
$report_db = '`'.$hub_db.'_annualreport`';
$hub_db = '`'.$hub_db.'`';
$mw_db = 'narwhal';
$net_db = 'network';

require_once ( JPATH_BASE .DS.'hubconfiguration.php');
$hconfig = new HUBConfig();

$db_net_host = $hconfig->ipDBHost;
$db_net_user = $hconfig->ipDBUsername;
$db_net_pass = $hconfig->ipDBPassword;
$net_db = $hconfig->ipDBDatabase;

*/

?>
