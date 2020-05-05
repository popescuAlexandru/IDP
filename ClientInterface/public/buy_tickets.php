
<div class="container">
    <?php include "templates/header.php"; ?>
    <img src="images/car.jpg" id="bg" alt="">
    <div class="text-block">
      <form method="post">
        <label for="booking_id">Booking ID</label>
        <input type="text" name="booking_id" id="booking_id" required>

        <label for="credit_card">Credit Card Details</label>
        <input type="text" name="credit_card" id="credit_card" required>

        <input type="submit" name="submit" value="Submit">

        <?php
        require "common.php";

        if (isset($_POST['submit'])) {
            $url = 'http://client_service:16000/buy_ticket?reservation_id=' . urlencode($_POST["booking_id"]) . '&credit_card=' . urlencode($_POST["credit_card"]);

            $options = array(
                'http' => array(
                    'header'  => "Content-type: application/json\r\n",
                    'method'  => 'GET',
                )
            );

            $context  = stream_context_create($options);
            $result = file_get_contents($url, false, $context);

            $json_result = json_decode($result, true);
            $boarding_pass = $json_result['boarding_pass'];
            $status = $json_result['status'];
            echo "<br>" . "<br>" . $status;
            if ($status === 'OK') {
                echo nl2br($boarding_pass);
            }
        }
        ?>

      </form>
      <a href="index.php">Back to home</a>
    </div>
    <?php include "templates/footer.php"; ?>
</div>
