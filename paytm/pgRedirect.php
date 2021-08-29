<?php

include("../include/db.php");
$createddate = date("Y-m-d h:i:s");
$ORDER_ID = $_POST["ORDER_ID"];
$M_ID = $_POST["M_ID"];
$CUST_ID = $_POST["CUST_ID"];
$u_mobileno = $_POST["u_mobileno"];
$pg_name = $_POST["pg_name"];
$TXN_AMOUNT = $_POST["TXN_AMOUNT"];
$u_datelimit_n = $_POST["u_datelimit_n"];
$EMAIL = $_POST["u_email"];
$message = $u_datelimit_n;

//api call ft_eventlog
$data = array(
	'credit' => $TXN_AMOUNT,
	'debit' => "0",
	'txn_id' => "",
	'odr_id' => $ORDER_ID,
	'pg_name' => $pg_name,
	'bank_name' => "",
	'comment' => "payment process for gateway",
	'status' => "failure",
	'createddate' => $createddate,
	'u_id' => $CUST_ID,
	'm_id' => $M_ID,


);

$curl = curl_init();

curl_setopt_array($curl, array(
  CURLOPT_URL => "http://103.146.110.30/topup/api/ft_transactions.php",
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => "",
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 30,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => "POST",
  CURLOPT_POSTFIELDS => json_encode($data),
  CURLOPT_HTTPHEADER => array(
    "cache-control: no-cache",
    "content-type: application/json"
  ),
));

$response = curl_exec($curl);
$err = curl_error($curl);

curl_close($curl);

/* if ($err) {
  echo "cURL Error #:" . $err;
} else {
  echo $response;
} */


//end data insert
$checkSum = "";
$paramList = array();
require_once("./lib/config_paytm.php");
require_once("./lib/encdec_paytm.php");
$INDUSTRY_TYPE_ID = "Retail";
$CHANNEL_ID = "WEB";
$paramList["MID"] = PAYTM_MERCHANT_MID;
$paramList["ORDER_ID"] = $ORDER_ID;
$paramList["CUST_ID"] = $CUST_ID;
$paramList["INDUSTRY_TYPE_ID"] = $INDUSTRY_TYPE_ID;
$paramList["CHANNEL_ID"] = $CHANNEL_ID;
$paramList["TXN_AMOUNT"] = $TXN_AMOUNT;
$paramList["WEBSITE"] = PAYTM_MERCHANT_WEBSITE;
$paramList["CALLBACK_URL"] = $h_add."/".$pg_name."/pgResponse.php";
$paramList["MSISDN"] = $u_mobileno; //Mobile number of customer
$paramList["EMAIL"] = $EMAIL; //Email ID of customer
$paramList["VERIFIED_BY"] = "EMAIL"; //
$paramList["IS_USER_VERIFIED"] = "YES"; //
$checkSum = getChecksumFromArray($paramList,PAYTM_MERCHANT_KEY);

?>

<html>
<head>
<title>Merchant Check Out Page</title>
</head>
<body>
	<center><h1>Please do not refresh this page...</h1></center>

		<form method="post" action="<?php echo PAYTM_TXN_URL ?>" name="f1">
		<table border="0">
			<tbody>
			<?php
			foreach($paramList as $name => $value) {
				echo '<input type="hidden" name="' . $name .'" value="' . $value . '">';
			}
			?>
			<input type="hidden" name="CHECKSUMHASH" value="<?php echo $checkSum ?>">
						
			</tbody>
		</table>
		<script type="text/javascript">
			document.f1.submit();
		</script>
	</form>
</body>
</html>