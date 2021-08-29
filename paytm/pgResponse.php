<script language="javascript" type="text/javascript">
    window.history.forward();
  </script>
<?php
// Include config file
include("../include/db.php");
// following files need to be included
$ORDERID = $_POST["ORDERID"];
$TXNAMOUNT = $_POST["TXNAMOUNT"];
$txnid=$_POST["TXNID"];
$paytmChecksum = "";
$paramList = array();
$isValidChecksum = "FALSE";
if ($_POST["STATUS"] == "TXN_SUCCESS") {
$status="success";}
else{$status="failure";}

require_once("./lib/config_paytm.php");
require_once("./lib/encdec_paytm.php");
$paramList = $_POST;
$paytmChecksum = isset($_POST["CHECKSUMHASH"]) ? $_POST["CHECKSUMHASH"] : ""; //Sent by Paytm pg
$isValidChecksum = verifychecksum_e($paramList, PAYTM_MERCHANT_KEY, $paytmChecksum); //will return TRUE or FALSE string.

if($isValidChecksum == "TRUE") {
	///////////
include("../include/date_update.php");
//////////
if ($_POST["STATUS"] == "TXN_SUCCESS") {
	$status="success";}
	else{$status="failure";}
}
	?>
	<form method="POST" action="../thankyou.php" name="f1">
	<input type="hidden" name="TXNID" value="<?php echo $txnid; ?>">
	<input type="hidden" name="status" value="<?php echo $status; ?>">
	<input type="hidden" name="expr_date" value="<?php echo $new_exp_date; ?>">
	<script type="text/javascript">
		document.f1.submit();
		</script>
	</form>

