<!DOCTYPE html>
<html>
<head/>
<body>
<?php 
/*Copyright 2014 Herve BUHLER, David LUCAS, Fabien NOLLET, Axel RESZETKO

Permission is hereby granted, without written agreement or royalty fee, to

use, copy, modify, and distribute this software and its documentation for

any purpose, provided that the above copyright notice and the following

three paragraphs appear in all copies of this software.


IN NO EVENT SHALL AUTHORS BE LIABLE TO ANY PARTY FOR DIRECT,

INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 

USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF AUTHORS HAVE

BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


AUTHORS SPECIFICALLY DISCLAIM ANY WARRANTIES INCLUDING, BUT NOT

LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A

PARTICULAR PURPOSE, AND NON-INFRINGEMENT.


THE SOFTWARE IS PROVIDED ON AN "AS-IS" BASIS AND AUTHORS HAVE NO

OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR

MODIFICATIONS.*/

function isAdmin(){
	if (isset($_SESSION[userID])){
		$userID = $_SESSION[userID] ;	
	try {
		$db = new PDO("mysql:host=localhost;dbname=dbname", "username", "password") ;
		$stmt =  $db->prepare("SELECT * FROM user WHERE id =?") ;
		$stmt->bindValue(1, $userId, PDO::PARAM_INT) ;
		$stmt->execute();
		$result = $stmt->fetch(PDO::FETCH_ASSOC) ;
		
		if ($result[role] === 'admin')
			return 1 ;
		$dbh = null;
	}
	catch(PDOException $e){
		return 0 ; 
		}
	}
	return 0 ;
}

$action = $_GET['action'] ;
$admin = isAdmin() ;

if ($action === 'admin_GetData' && $admin == 1){
	try {
		$db = new PDO("mysql:host=localhost;dbname=dbname", "username", "password") ;
		$stmt =  $db->prepare("SELECT * FROM user") ;
		$stmt->execute();
		$result = $stmt->fetchAll(PDO::FETCH_ASSOC) ;
		print_r($result);
	}
	catch(PDOException $e){
		echo $e->getMessage() ;
		}	
	}
	
if ($action === 'GetData'){
	echo "DATA" ;
	}
?>


<h1>Hello World!</h1>
</body>
</html>
