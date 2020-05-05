<?php
require "common.php";

if (isset($_POST['submit'])) {
	$url = 'http://client_service:16000/get_optimal_route?source=' . urlencode($_POST["source"]) . '&dest=' . urlencode($_POST["dest"]) . '&departure_day=' . urlencode($_POST["departure_day"]) . '&max_rides=' . urlencode($_POST["max_rides"]);

	$options = array(
		'http' => array(
		    'header'  => "Content-type: application/json\r\n",
		    'method'  => 'GET',
		)
	);

	$context  = stream_context_create($options);
	$result = file_get_contents($url, false, $context);

	$json_result = json_decode($result, true);
	$route = $json_result['route'];
	$status = $json_result['status'];
	echo $status;
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
        <input type="number" name="departure_day" id="departure_day" min="1" required>

        <label for="max_rides">Maximum number of rides</label>
        <input type="number" name="max_rides" id="max_rides" min="1" required>

        <input type="submit" name="submit" value="Submit">

        <?php
        if ($status === 'OK') { ?>
                <h2>Route</h2>

                <table>
                    <thead>
                        <tr>
                            <th>Ride ID</th>
                            <th>Source Name</th>
                            <th>Destination Name</th>
                            <th>Departure Day</th>
                            <th>Departure Hour</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($route[1] as $row) { ?>
                            <tr>
                                <td><?php echo escape($row[2]); ?></td>
                                <td><?php echo escape($row[3]); ?></td>
                                <td><?php echo escape($row[4]); ?></td>
                                <td><?php echo escape($row[0]); ?></td>
                                <td><?php echo escape($row[1]); ?></td>
                                <td><?php echo escape($row[5]); ?></td>
                            </tr>
                        <?php } ?>
                    </tbody>
                </table>
        <?php } ?>
      </form>
      <a href="index.php">Back to home</a>
    </div>
    <?php include "templates/footer.php"; ?>
</div>
