var button_pressed = "";
 $("button").click(function() {
    button_pressed = this.id;

});

$(document).ready(function() {


  //on select user / select operator

  $("select#u_p_name_for_ticket").change(function(){

      // var u_id = $(this).children("option:selected").val();
      var u_id = $(this).find(":selected").val();

      //op_id filling

      var op_id = get_op_id_from_u_id(u_id);


      if($('#op_id').prop('type') != 'hidden' && op_id!=null && op_id){

          $('#op_id').val(op_id);

          //instance filling

          var get_data = get_instance_from_op_id(op_id);

          $('#instance_id').html(`<option value="0">None</option>`);

          for (i = 0; i < get_data.length; i++) {

               $('#instance_id').append(`<option value="${get_data[i].id}"> 
                              ${get_data[i].username}
                          </option>`);

            }


      }



      

  });


//on operator select show instance

$("select#op_id").change(function(){


          var op_id = $(this).children("option:selected").val();


            //instance filling

            var get_data = get_instance_from_op_id(op_id);

            $('#instance_id').html(`<option value="0">None</option>`);

            for (i = 0; i < get_data.length; i++) {

                 $('#instance_id').append(`<option value="${get_data[i].id}"> 
                                ${get_data[i].username}
                            </option>`);

              }




});





//Create ticket Start

var ticket_create = $("#ticket_create");
ticket_create.on('submit', function(e) {
    e.preventDefault(); // prevent default form submit

     if(button_pressed != 'ticket_create_btn')
    {
       toastr.error('Invalid Request..!');
       return false;
    }

    

    var u_id = $("#u_p_name_for_ticket").val();
    var subject = $("#subject").val();
    var message = $("#message").val();
    var priority = $("#priority").val();
    var group = $("#group").val();
    var ticket_due_date = $("#ticket_due_date").val();
    var op_id = $("#op_id").val();
    var instance_id = $("#instance_id").val();

   
    



  if(!u_id || u_id == "" || subject == "" || message == "" || priority == "" || group == "" || ticket_due_date == "" || op_id == "" || instance_id == "")
  {
      toastr.error('Please Fill Atleast (*) Mendatory Values.');
      return false;
  }
  else if(priority < 0 || priority > 3)
  {
      toastr.error('Please Select Valid Priority.');
      return false;
  }
  else if(group < 0 || group > 1)
  {
      toastr.error('Please Select Valid Group.');
      return false;
  }


  $("#"+button_pressed).attr("disabled", "disabled");
  $("#"+button_pressed).html("<i class='fa fa-refresh'></i>&nbsp;&nbsp;Wait..");

            var formData = new FormData(this);

            formData.append('action', 'ticket_create');


          $.ajax({
            url: 'controller/ticket.php', 
            type: 'POST', 
            dataType: 'html',
            data:  formData,
            contentType: false,
            cache: false, 
            processData: false,
            // data: ticket_create.serialize() + '&action=ticket_create', 
            
            success: function(data) {
              var response = JSON.parse(data);
              if(response[0] == "success")
              {
                
                  toastr.options.onHidden = function() { window.location.href = response[2]; }
                  toastr.success(response[1]);
              }
              else
              {
              
               
                 toastr.error(response);
                 $("#"+button_pressed).removeAttr("disabled");
                 $("#"+button_pressed).html("<i class='fa fa-plus'></i>&nbsp;&nbsp;Create");
               

                   
              }
              

        
            },
           
          });



      
      

   });

    // Create ticket Finish


    //Update ticket Start

var ticket_update = $("#ticket_update");
ticket_update.on('submit', function(e) {
    e.preventDefault(); // prevent default form submit

     if(button_pressed != 'ticket_update_btn')
    {
       toastr.error('Invalid Request..!');
       return false;
    }

    
    var ticket_id = $("#ticket_id").val();
    var subject = $("#subject").val();
    var priority = $("#priority").val();
    var group = $("#group").val();
    var ticket_due_date = $("#ticket_due_date").val();



  if(ticket_id <= 0 || ticket_id == "")
  {
      toastr.error('Invalid Request.');
      return false;
  }
  else if(subject == "" || priority == "" || group == "" || ticket_due_date == "")
  {
      toastr.error('Please Fill Atleast (*) Mendatory Values.');
      return false;
  }
  else if(priority < 0 || priority > 3)
  {
      toastr.error('Please Select Valid Priority.');
      return false;
  }
  else if(group < 0 || group > 1)
  {
      toastr.error('Please Select Valid Group.');
      return false;
  }


  $("#"+button_pressed).attr("disabled", "disabled");
  $("#"+button_pressed).html("<i class='fa fa-refresh'></i>&nbsp;&nbsp;Wait..");


          $.ajax({
            url: 'controller/ticket.php', 
            type: 'POST', 
            dataType: 'html',
            data: ticket_update.serialize() + '&action=ticket_update',
            
            success: function(data) {
              var response = JSON.parse(data);
              if(response[0] == "success")
              {
                
                  toastr.options.onHidden = function() { window.location.reload(); }
                  toastr.success(response[1]);
              }
              else
              {
              
               
                 toastr.error(response);
                 $("#"+button_pressed).removeAttr("disabled");
                 $("#"+button_pressed).html("<i class='fa fa-pencil'></i>&nbsp;&nbsp;Update");
               

                   
              }
              

        
            },
           
          });



      
      

   });

    // Update ticket Finish





      /* ########################## Status Change Action Start ################ */


        

  //Reassing Ticket

  $( "#ticket_reassign_btn" ).click(function() {
  
              $('#ticket_reassign_modal').modal('show');

      });



    //Ticket Reassing submit

      var ticket_reassign_frm  = $('#ticket_reassign_frm');
      ticket_reassign_frm.on('submit', function(e) {
        e.preventDefault(); // prevent default form submit
        

                $('#ticket_reassign_modal').modal('hide');
                var op_id = $('#op_id').val();
                var instance_id = $('#instance_id').val();

                if(op_id == '' || op_id < 0 || instance_id < 0)
                {
                    toastr.error('Please Fill Atleast (*) Mendatory Values.');
                     return false;
                }

              $.ajax({
                url: 'controller/ticket.php', // form action url
                type: 'POST', // form submit method get/post
                dataType: 'html', // request type html/json/xml
                data:  ticket_reassign_frm.serialize() + '&action=ticket_reassign',  // serialize form data
                // dataType: 'json', 
                success: function(data) {

                  var response = JSON.parse(data);
                  if(response[0] == 'success')
                  {
 
                      toastr.options.onHidden = function() { window.location.reload(); }
                      toastr.success(response[1]);

                  }
                  else
                  {
                  
                    toastr.error(response);
       
                  }
                  

            
                },
               
              });



      });


  //Resolve Ticket

  $( "#ticket_resolve_btn" ).click(function() {
  
              $('#ticket_resolve_modal').modal('show');

      });


  //Ticket Resolve submit

      var ticket_resolve_frm  = $('#ticket_resolve_frm');
      ticket_resolve_frm.on('submit', function(e) {
        e.preventDefault(); // prevent default form submit
        

            $('#ticket_resolve_modal').modal('hide');


              $.ajax({
                url: 'controller/ticket.php', // form action url
                type: 'POST', // form submit method get/post
                dataType: 'html', // request type html/json/xml
                data:  ticket_resolve_frm.serialize() + '&action=ticket_resolve',  // serialize form data
                // dataType: 'json', 
                success: function(data) {

                  var response = JSON.parse(data);
                  if(response[0] == 'success')
                  {
 
                      toastr.options.onHidden = function() { window.location.reload(); }
                      toastr.success(response[1]);

                  }
                  else
                  {
                  
                    toastr.error(response);
       
                  }
                  

            
                },
               
              });



      });




  //Close Ticket

  $( "#ticket_close_btn" ).click(function() {


            //check otp verification is on or not

            var ticket_id = $(this).data("tid");

            $.ajax({
                url: 'controller/ticket.php', // form action url
                type: 'POST', // form submit method get/post
                dataType: 'html', // request type html/json/xml
                data:  'action=check_ticket_close_otp_ver&ticket_id=' + ticket_id,  // serialize form data
                // dataType: 'json', 
                success: function(data) {

                  var response = JSON.parse(data);
                  if(response[0] == 'success')
                  {
 
                      if(response[1] == '1')
                      {
                            if(!confirm("Are you sure? System will send OTP to the customer for verification.")){
            
                                return false;
                            }
                            else
                            {
                                var send_otp_res = send_ticket_close_otp(ticket_id);

                                if(send_otp_res == 'success')
                                {
                                    $('#ticket_close_modal').modal('show');
                                }
                                else
                                {
                                    toastr.error(response);
                                    return false;
                                }

                                
                            }
                      }
                      else
                      {
                          $('#ticket_close_modal').modal('show');
                      }

                  }
                  else
                  {
                  
                    toastr.error(response);
                    return false;
       
                  }
                  

            
                },
               
              });


  
              

      });


    //Ticket close submit

      var ticket_close_frm  = $('#ticket_close_frm');
      ticket_close_frm.on('submit', function(e) {
        e.preventDefault(); // prevent default form submit
              
              

              $.ajax({
                url: 'controller/ticket.php', // form action url
                type: 'POST', // form submit method get/post
                dataType: 'html', // request type html/json/xml
                data:  ticket_close_frm.serialize() + '&action=ticket_close',  // serialize form data
                // dataType: 'json', 
                success: function(data) {

                  var response = JSON.parse(data);
                  if(response[0] == 'success')
                  {

                      $('#ticket_close_modal').modal('hide');
 
                      toastr.options.onHidden = function() { window.location.reload(); }
                      toastr.success(response[1]);

                  }
                  else
                  {
                  
                    toastr.error(response);
       
                  }
                  

            
                },
               
              });



      });


  //reopen Ticket

  $( "#ticket_reopen_btn" ).click(function() {
  
              $('#ticket_reopen_modal').modal('show');

      });


    //Ticket reopen submit

      var ticket_reopen_frm  = $('#ticket_reopen_frm');
      ticket_reopen_frm.on('submit', function(e) {
        e.preventDefault(); // prevent default form submit
              
              $('#ticket_reopen_modal').modal('hide');

              $.ajax({
                url: 'controller/ticket.php', // form action url
                type: 'POST', // form submit method get/post
                dataType: 'html', // request type html/json/xml
                data:  ticket_reopen_frm.serialize() + '&action=ticket_reopen',  // serialize form data
                // dataType: 'json', 
                success: function(data) {

                  var response = JSON.parse(data);
                  if(response[0] == 'success')
                  {
 
                      toastr.options.onHidden = function() { window.location.reload(); }
                      toastr.success(response[1]);

                  }
                  else
                  {
                  
                    toastr.error(response);
       
                  }
                  

            
                },
               
              });



      });



  //add_comment Ticket

  $( "#ticket_add_comment_btn" ).click(function() {
  
              $('#ticket_add_comment_modal').modal('show');

      });


  //Ticket add comment submit

      var ticket_add_comment_frm  = $('#ticket_add_comment_frm');
    ticket_add_comment_frm.on('submit', function(e) {
        e.preventDefault(); // prevent default form submit


            $('#ticket_add_comment_modal').modal('hide');

            var formData = new FormData(this);

            formData.append('action', 'ticket_add_comment');
            

          
              $.ajax({
                url: 'controller/ticket.php', // form action url
                type: 'POST', // form submit method get/post
                dataType: 'html', // request type html/json/xml
                data:  formData,
                contentType: false,
                cache: false, 
                processData: false,
                
                success: function(data) {

                  var response = JSON.parse(data);
                  if(response[0] == 'success')
                  {
 
                      toastr.options.onHidden = function() { window.location.reload(); }
                      toastr.success(response[1]);

                  }
                  else
                  {
                  
                    toastr.error(response);
       
                  }
                  

            
                },
               
              });



      });


      /* ########################## Status Change Action End ################ */



      //Ticket Delete Start
      $( ".ticket_delete_btn" ).click(function(){


        if (!confirm("Are you sure to delete this Ticket ?")){
            
                return false;
            }

        var ticket_id = $(this).attr('id');

        if(ticket_id == "")
        {
            toastr.error('Invalid Ticket.');
            return false;
        }
          $("#"+ticket_id).html("<i class='fa fa-refresh'></i>&nbsp;&nbsp;Wait..");
               $.ajax({
            url: 'controller/ticket.php', // form action url
            type: 'POST', // form submit method get/post
            dataType: 'html', // request type html/json/xml
            data:{ticket_id:ticket_id,action:'ticket_delete'},  // serialize form data

            success: function(data) {
              var response = JSON.parse(data);
              if(response[0] == 'success')
              {
                    
                    toastr.options.onHidden = function() { window.location.href = response[2]; }
                    toastr.success(response[1]);

              }
              else
              {
               
               toastr.error(response);
               $("#"+ticket_id).html("<i class='fa fa-trash'></i>&nbsp;&nbsp;Delete");
    
   
              }
              

        
            },
           
          });

              

      }); 
      //Ticket Delete Finish


      //Ticket Delete From Table start

      $( "#ticket_list_tbl" ).on("click", ".ticket_delete_btn", function(){


        if (!confirm("Are you sure to delete this Ticket ?")){
            
                return false;
            }

        var ticket_id = $(this).attr('id');

        if(ticket_id == "")
        {
            toastr.error('Invalid Ticket.');
            return false;
        }
          $("#"+ticket_id).html("<i class='fa fa-refresh'></i>&nbsp;&nbsp;Wait..");
               $.ajax({
            url: 'controller/ticket.php', // form action url
            type: 'POST', // form submit method get/post
            dataType: 'html', // request type html/json/xml
            data:{ticket_id:ticket_id,action:'ticket_delete'},  // serialize form data

            success: function(data) {
              var response = JSON.parse(data);
              if(response[0] == 'success')
              {
                    
                    toastr.options.onHidden = function() { window.location.href = response[2]; }
                    toastr.success(response[1]);

              }
              else
              {
               
               toastr.error(response);
               $("#"+ticket_id).html("<i class='fa fa-trash'></i>&nbsp;&nbsp;Delete");
    
   
              }
              

        
            },
           
          });

              

      }); 

      //Ticket Delete From Table Finish







});





//get instance data from op_id


function get_instance_from_op_id(op_id)
{         

          var response;

            $.ajax({

                async: false,
                url: 'controller/ticket.php', 
                type: 'POST',
                dataType: 'html',
                data: 'action=get_instance_from_op_id&op_id='+op_id,  
                success: function(data) {

                  response = JSON.parse(data);

                },


               
              });

            return response;
}

function get_op_id_from_u_id(u_id)
{         

          var response;

            $.ajax({

                async: false,
                url: 'controller/ticket.php', 
                type: 'POST',
                dataType: 'html',
                data: 'action=get_op_id_from_u_id&u_id='+u_id,  
                success: function(data) {

                  response = JSON.parse(data);

                },


               
              });

            return response;
}


function send_ticket_close_otp(ticket_id)
{

          var response = "";

          $.ajax({

                async: false,
                url: 'controller/ticket.php', 
                type: 'POST',
                dataType: 'html',
                data: 'action=send_ticket_close_otp&ticket_id='+ticket_id,  
                success: function(data) {

                  response = JSON.parse(data);

                },


               
              });

            return response;
}