<?php

if (isset($_POST['submit'])) {
	$url = 'http://localhost:15000/add_ride';
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

	echo $result;
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
        <input type="number" name="departure_day" id="departure_day" min="1" max="365">

        <label for="departure_hour">Departure Hour</label>
        <input type="number" name="departure_hour" id="departure_hour" min="0" max="23">

        <label for="duration">Duration</label>
        <input type="number" name="duration" id="duration" min="0">

        <label for="price">Price</label>
        <input type="number" name="price" id="price" min="1">

        <label for="number_of_seats">Number of Seats</label>
        <input type="number" name="number_of_seats" id="number_of_seats" min="1">

        <label for="ride_id">Ride ID</label>
        <input type="text" name="ride_id" id="ride_id">

        <input type="submit" name="submit" value="Submit">
      </form>
      <a href="index.php">Back to home</a>
    </div>
    <?php include "templates/footer.php"; ?>
</div>
