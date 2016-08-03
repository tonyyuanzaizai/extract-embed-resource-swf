<?php
set_time_limit(0); 

define( 'PATH_ROOT', dirname(__FILE__).'/' );
$fileOutput = PATH_ROOT . 'output/';
mkdir($fileOutput, 0700);

function normalizeName($strname){
    $idx = strpos($strname, '$');
    if($idx > 0){
        $strname = substr($strname, 0, $idx);
        $idx = strrpos($strname, '_');
        $strname = substr($strname, 0, $idx) . '.'. substr($strname, $idx+1);
    }
    
    return $strname;
}

function test_normalizeName(){
    $tname = 'JJ_Episode5Layout_xml$531d5e5d424cc9522da87717e5d07774720432878';
    echo normalizeName($tname);
}

function fixXML($xml_file){
	$content_arr = array();
	$doc = new DOMDocument();
	$doc->load($xml_file);
	$data = $doc->childNodes->item(0);
		
	$DefineSound_list = $data->getElementsByTagName('DefineSound');//mp3
	$DefineBinaryData_list = $data->getElementsByTagName('DefineBinaryData');//xml, json,...
	$DefineBitsJPEG2_list = $data->getElementsByTagName('DefineBitsJPEG2');//png,jpg
	$Symbol_list = $data->getElementsByTagName('SymbolClass')->item(0)->getElementsByTagName('Symbol');//SymbolClass
	
	$symbolArr = array();
	for( $i=0; $i < $Symbol_list->length; $i++){
		$dataChild = $Symbol_list->item($i);		
		
		if($dataChild instanceof DOMElement && $dataChild->nodeType == 1){
			$objectID    = $dataChild->getAttribute('objectID');
			$objectName  = $dataChild->getAttribute('name');
            $objectName = normalizeName($objectName);
            $symbolArr[$objectID] = $objectName;
		}
	}
	
	$byteDataArr = array();
	// get all types
	for( $i=0; $i < $DefineSound_list->length; $i++){
		$dataChild = $DefineSound_list->item($i);		
		
		if($dataChild instanceof DOMElement && $dataChild->nodeType == 1){
			$objectID    = $dataChild->getAttribute('objectID');
			$objectVal =  $dataChild->getElementsByTagName('data')->item(0)->nodeValue;
			$byteDataArr[$objectID] = $objectVal;
		}
	}
	
	for( $i=0; $i < $DefineBinaryData_list->length; $i++){
		$dataChild = $DefineBinaryData_list->item($i);		
		
		if($dataChild instanceof DOMElement && $dataChild->nodeType == 1){
			$objectID    = $dataChild->getAttribute('objectID');
			$objectVal =  $dataChild->getElementsByTagName('data')->item(0)->nodeValue;
			$byteDataArr[$objectID] = $objectVal;
		}
	}
	for( $i=0; $i < $DefineBitsJPEG2_list->length; $i++){
		$dataChild = $DefineBitsJPEG2_list->item($i);		
		
		if($dataChild instanceof DOMElement && $dataChild->nodeType == 1){
			$objectID    = $dataChild->getAttribute('objectID');
			$objectVal =  $dataChild->getElementsByTagName('data')->item(0)->nodeValue;
			$byteDataArr[$objectID] = $objectVal;
		}
	}
	
	//array_keys($byteDataArr as $key=>$val);
	foreach($byteDataArr as $key=>$val){
	    $objectName = $symbolArr[$key];
	    $objectVal  = $val;
	    if(!empty($objectName) && !empty($objectVal)){
	        file_put_contents(PATH_ROOT. 'output/'.$objectName, base64_decode($objectVal));
	    }
	}
}

fixXML('game.xml');
?>