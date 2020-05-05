<script src="//ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>

<div class="container">
    <?php include "templates/header.php"; ?>
    <img src="images/car.jpg" id="bg" alt="">
    <div class="text-block">
        <?php
        require "common.php";

        if (isset($_POST['submit'])) {
            $url = 'http://client_service:16000/book_ticket?';

            foreach ($_POST['name'] as $id) {
                $url = $url . 'ride_ids[]=' . urlencode($id) . '&';
            }
            $url = rtrim($url, "&");

            $context  = stream_context_create($options);
            $result = file_get_contents($url, false, $context);

            $json_result = json_decode($result, true);
            $booking_id = $json_result['booking_id'];
            $status = $json_result['status'];
            echo $status . "<br>" . $booking_id;
        }
        ?>
        <form name="add_id" id="add_id" method="post">
            <table id="dynamic_field">
                <tr>
                    <td><input type="text" name="name[]" placeholder="Enter Ride ID" required="" /></td>
                    <td><button type="button" name="add" id="add" >Add More</button></td>
                </tr>
            </table>
            <input type="submit" name="submit" value="Submit" id="submit">
        </form>

      <a href="index.php">Back to home</a>
    </div>
    <?php include "templates/footer.php"; ?>
</div>

<script type="text/javascript">
    $(document).ready(function(){
      var postURL = "/book_rides.php";
      var i=1;


      $('#add').click(function(){
           i++;
           $('#dynamic_field').append('<tr id="row'+i+'" class="dynamic-added"><td><input type="text" name="name[]" placeholder="Enter Ride ID" required /></td><td><button type="button" name="remove" id="'+i+'" class="btn btn-danger btn_remove">X</button></td></tr>');
      });


      $(document).on('click', '.btn_remove', function(){
           var button_id = $(this).attr("id");
           $('#row'+button_id+'').remove();
      });


      $('#submit').click(function(){
           $.ajax({
                url:postURL,
                method:"POST",
                data:$('#add_name').serialize(),
                type:'json',
                success:function(data)
                {
                  	i=1;
                  	$('.dynamic-added').remove();
                  	$('#add_name')[0].reset();
                }
           });
      });


    });
</script>