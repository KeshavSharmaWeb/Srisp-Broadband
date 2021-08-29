var button_pressed = "";
 $("button").click(function() {
    button_pressed = this.id;

});

$(document).ready(function() {
  
  

$('input[name="recharge_type"]').click(function() {
       if($(this).prop('id') == 'online_payment') {
            $('#recharge_with_online').show();
            $('#recharge_with_code').hide();
                  
       }

       else if($(this).prop('id') == 'code_payment') {
            $('#recharge_with_code').show();
            $('#recharge_with_online').hide();   
       }
   });


//Prepare srv data

$('#s_id').on('change', function() {

  var s_id = this.value;
  // console.log(s_id);

    $.ajax({
      url: 'controller/recharge_topup.php', 
      type: 'POST',
      dataType: 'html',
      data: 'action=prepare_data_from_sid&s_id='+s_id, 
      success: function(data) {

          var response = JSON.parse(data);

          if(response.status == 'success')
          {
               
                $('#totallimit').html(response.totallimit);
                $('#datelimit').html(response.datelimit);
                $('#onlinelimit').html(response.onlinelimit);
                $('#price').html(response.price);

                var rate = response.downrate + ' / ' + response.uprate;

                $('#rate').html(rate);
                if(response.pricewithtax == 1)
                {
                    $('#pricewithtax').html('Yes');
                }
                else
                {
                    $('#pricewithtax').html('No');
                }

          }
          else
          {
              toastr.error(response.status);
          }


    
      },
     
    });


});

//check use wallet

 $('#use_wallet').click(function(){
            if($(this).prop("checked") == true){
                
                $('#wallet_money').show();
                $('#payable_amount').show();

            }
            else if($(this).prop("checked") == false){
              

              $('#wallet_money').hide();
                $('#payable_amount').hide();

            }
        });



//Check Press enter

// $('#recharge_quantity').keypress(function (e) {
//  var key = e.which;
//  if(key == 13)  // the enter key code
//   {
//     $('#online_recharge_btn').click();
//     return false;  
//   }
// });



// check recharge data

  
  // $('#online_recharge_btn').on('click', function() {

  // var s_id = $('#s_id').val();
  // var recharge_quantity = $('#recharge_quantity').val();


  // if(recharge_quantity <= 0)
  // {
  //     toastr.error('Please Enter Valid Recharge Quantity.');
  //     return false;
  // }

  
  // console.log(s_id);

  



  //Proceed to pay

  


    //Recharge with code

        var code_recharge_frm = $("#code_recharge_frm");
      code_recharge_frm.on('submit', function(e) {
        e.preventDefault(); // prevent default 

        if(button_pressed != 'code_recharge_btn')
        {
           toastr.error('Invalid Request..!');
           return false;
        }

        
        $("#"+button_pressed).attr("disabled", "disabled");
        $("#"+button_pressed).html("<i class='fa fa-refresh'></i>&nbsp;&nbsp;Wait..");

        var recharge_code = $('#recharge_code').val();

        if(recharge_code == "" || !recharge_code)
        {
          $("#"+button_pressed).removeAttr("disabled");
            $("#"+button_pressed).html("<i class='fa fa-check'></i>&nbsp;&nbsp;Recharge");
            toastr.error('Please Enter Valid Recharge Code.'); 
            return false;
        }

        $.ajax({
          url: 'controller/recharge_topup.php', 
          type: 'POST',
          dataType: 'html',
          data: code_recharge_frm.serialize() + '&action=recharge_with_code', 
          success: function(data) {
              var response = JSON.parse(data);
              if(response[0] == 'success')
              {
      
                      document.location = response[1];
              }
              else
              {
                  $("#"+button_pressed).removeAttr("disabled");
                  $("#"+button_pressed).html("<i class='fa fa-check'></i>&nbsp;&nbsp;Recharge");
                  toastr.error(response); 
              }


        
          },
         
        });


    });

  






});

