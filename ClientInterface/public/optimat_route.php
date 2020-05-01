<?php

if (isset($_POST['submit'])) {
	$url = 'http://localhost:16000/get_optimal_route';
	$data = array(  'source' => $_POST["source"],
					'dest' => $_POST["dest"],
					'departure_day' => $_POST["departure_day"],
					'max_flights' => $_POST["departure_hour"]
			);

	$options = array(
		'http' => array(
		    'header'  => "Content-type: application/json\r\n",
		    'method'  => 'GET',
		    'content' => json_encode($data)
		)
	);

	$context  = stream_context_create($options);
	$result = file_get_contents($url, false, $context);

	$json_result = json_decode($result, true);
	echo $json_result['status'];
}
?>

<div class="container">
    <?php include "templates/header.php"; ?>
    <img src="images/car.jpg" id="bg" alt="">
    <div class="text-block">
      <form method="post">
        <label for="source">Source Name</label>
        <input type="text" name="source" id="source">

        <label for="dest">Destination Name</label>
        <input type="text" name="dest" id="dest">

        <label for="departure_day">Departure Day</label>
        <input type="number" name="departure_day" id="departure_day" min="1">

        <label for="max_rides">Maximum number of rides</label>
        <input type="number" name="max_rides" id="max_rides" min="1">

        <input type="submit" name="submit" value="Submit">
      </form>
      <a href="index.php">Back to home</a>
    </div>
    <?php include "templates/footer.php"; ?>
</div>
