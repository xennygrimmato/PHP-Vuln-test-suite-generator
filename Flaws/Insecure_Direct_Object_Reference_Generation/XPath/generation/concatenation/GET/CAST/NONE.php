<?php 
/*Unsafe sample
construction : concatenation
input : reads the field UserData from the variable $_GET and uses intval() function
sanitize : NONE */

/*COPYRIGHT 2014 TN*/


$tainted = intval($_GET['id']);
$checked_data = $tainted
$query="//Course[@id=". $checked_data . "]";

$xml = simplexml_load_file("users.xml");
//flaw
$res=$xml->xpath($query);

?>