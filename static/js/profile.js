var button_pressed = "";
 $("button").click(function() {
    button_pressed = this.id;

});

$(document).ready(function() {


//Update User Profile

    var profile_update = $("#profile_update");
	profile_update.on('submit', function(e) {
    e.preventDefault(); // prevent default 

    if(button_pressed != 'profile_update_btn')
    {
       toastr.error('Invalid Request..!');
       return false;
    }

    
    $("#"+button_pressed).attr("disabled", "disabled");
    $("#"+button_pressed).html("<i class='fa fa-refresh'></i>&nbsp;&nbsp;Wait..");

    var u_fullname = $('#u_fullname').val();
    var u_address = $('#u_address').val();
    var u_city = $('#u_city').val();
    var u_zip = $('#u_zip').val();
    var u_state = $('#u_state').val();
    var u_country = $('#u_country').val();
    var u_mobileno = $('#u_mobileno').val();
    var u_email = $('#u_email').val();



    if(u_fullname == "" || u_address == "" || u_city == "" || u_zip == "" || u_state == "" || u_country == "" || u_mobileno == "")
    {
    	   $("#"+button_pressed).removeAttr("disabled");
      	 $("#"+button_pressed).html("<i class='fa fa-pencil'></i>&nbsp;&nbsp;Update");
      	 toastr.error('Please Fill Atleast (*) Mandatory Values.');
      	 return false;
    }
    else if(u_email != "" && !ValidateEmail(u_email))
    {
        $("#"+button_pressed).removeAttr("disabled");
         $("#"+button_pressed).html("<i class='fa fa-pencil'></i>&nbsp;&nbsp;Update");
         toastr.error("Please Enter Valid E-mail Address.");
         return false;
    }
    else if(!ValidateMobileNo(u_mobileno))
    {
         $("#"+button_pressed).removeAttr("disabled");
         $("#"+button_pressed).html("<i class='fa fa-pencil'></i>&nbsp;&nbsp;Update");
         toastr.error("Please Enter Valid Mobile No.");
         return false;
    }

    $.ajax({
      url: 'controller/profile.php', 
      type: 'POST',
      dataType: 'html',
      data: profile_update.serialize() + '&action=user_update_profile', 
      success: function(data) {
          var response = JSON.parse(data);
          if(response[0] == 'success')
          {
  
                  toastr.options.onHidden = function() { location.reload(); }
                  toastr.success(response[1]);
          }
          else
          {
              $("#"+button_pressed).removeAttr("disabled");
              $("#"+button_pressed).html("<i class='fa fa-pencil'></i>&nbsp;&nbsp;Update");
              toastr.error(response); 
          }


    
      },
     
    });


});



});