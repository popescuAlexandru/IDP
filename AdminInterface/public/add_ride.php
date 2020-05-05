<?php

if (isset($_POST['submit'])) {
	$url = 'http://adm_service:15000/add_ride';
	$data = array(  'source' => $_POST["source"],
					'dest' => $_POST["dest"],
					'departure_day' => $_POST["departure_day"],
					'departure_hour' => $_POST["departure_hour"],
					'duration' => $_POST["duration"],
					'price' => $_POST["price"],
					'number_of_seats' => $_POST["number_of_seats"],
					'ride_id' => $_POST["ride_id"]);

	$options = array(
		'http' => array(
		    'header'  => "Content-type: application/json\r\n",
		    'method'  => 'POST',
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
        <input type="text" name="source" id="source" required>

        <label for="dest">Destination Name</label>
        <input type="text" name="dest" id="dest" required>

        <label for="departure_day">Departure Day</label>
        <input type="number" name="departure_day" id="departure_day" min="1" max="365" required>

        <label for="departure_hour">Departure Hour</label>
        <input type="number" name="departure_hour" id="departure_hour" min="0" max="23" required>

        <label for="duration">Duration</label>
        <input type="number" name="duration" id="duration" min="0" required>

        <label for="price">Price</label>
        <input type="number" name="price" id="price" min="1" required>

        <label for="number_of_seats">Number of Seats</label>
        <input type="number" name="number_of_seats" id="number_of_seats" min="1" required>

        <label for="ride_id">Ride ID</label>
        <input type="text" name="ride_id" id="ride_id" required>

        <input type="submit" name="submit" value="Submit">
      </form>
      <a href="index.php">Back to home</a>
    </div>
    <?php include "templates/footer.php"; ?>
</div>
