<?php
    require "../common.php";

    if (isset($_GET["ride_id"])) {
        $url = 'http://localhost:15000/cancel_ride';
        $data = array('ride_id' => $_GET["ride_id"]);

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
        echo $json_result['status'] . "<br>";
    }

    $url = 'http://localhost:15000/list_rides';
	$data = array();

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
    $data = $json_result['data'];
	echo $json_result['status'];
?>

<div class="container">
    <?php include "templates/header.php"; ?>
    <img src="images/car.jpg" id="bg" alt="">
    <div class="text-block">
        <?php
            if ($result) { ?>
                <h2>Rides</h2>

                <table>
                    <thead>
                        <tr>
                            <th>Ride ID</th>
                            <th>Source Name</th>
                            <th>Destination Name</th>
                            <th>Departure Hour</th>
                            <th>Departure Day</th>
                            <th>Duration</th>
                            <th>Price</th>
                            <th>Number of Seats</th>
                            <th>Booked Tickets</th>
                            <th>Bought Tickets</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($data as $row) { ?>
                            <tr>
                                <td><?php echo escape($row[0]); ?></td>
                                <td><?php echo escape($row[1]); ?></td>
                                <td><?php echo escape($row[2]); ?></td>
                                <td><?php echo escape($row[3]); ?></td>
                                <td><?php echo escape($row[4]); ?></td>
                                <td><?php echo escape($row[5]); ?></td>
                                <td><?php echo escape($row[6]); ?></td>
                                <td><?php echo escape($row[7]); ?></td>
                                <td><?php echo escape($row[8]); ?></td>
                                <td><?php echo escape($row[9]); ?></td>
                            </tr>
                        <?php } ?>
                    </tbody>
                </table>
            <?php } else { ?>
                > No results found.
            <?php }
            ?>
        <a href="index.php">Back to home</a>
    </div>
    <?php include "templates/footer.php"; ?>
</div>

<?php require "templates/header.php"; ?>


<?php require "templates/footer.php"; ?>
