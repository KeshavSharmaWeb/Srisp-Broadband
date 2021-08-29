$(document).ready(function() {
  


  var login_form = $('#login_form'); 
  var login_submit = $('#login_button');
  var login_alert = $('#login_msg'); 


  

  // form submit event

  login_form.on('submit', function(e) {
    e.preventDefault(); 


    login_submit.attr('disabled','true');

    $.ajax({
      url: 'client/controller/auth.php', 
      type: 'POST',
      dataType: 'html',
      data: login_form.serialize() + '&action=login', 
      success: function(data) {
        var response = JSON.parse(data);
        if(response[0] == "success")
        {
          window.location.href = response[1];
        }
        else
        {

          login_submit.removeAttr('disabled');
         
          toastr.warning(response);

             
        }
        

  
      },
     
    });
  });

});