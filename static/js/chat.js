$('#error_msg').hide()
$('#chat_sub').on('click', function () {
    
    selected_ele = document.getElementById('msg_val');
    output = selected_ele.value;

    if(output != "") {

    tick = document.getElementById('tick_id');
    ticket_output = tick.value;

    u_id = document.getElementById('u_id');
    u_id_output = u_id.value;
    

    $.ajax({
        url: '/chat',
        type: 'POST',
        data: { msg_send: output, t_id : ticket_output, send_by : 'admin', u_id : u_id_output},
        success: function () {
            $('#msg_val').val('');
            $("#chat_panel").load(location.href+ " #chat_panel", );
            console.log('refreshed right now!')
        }
    });
    }
    else {
        $('#error_msg').show()
    }
});