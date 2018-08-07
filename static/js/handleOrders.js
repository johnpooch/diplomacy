$(document).ready(function() {
    $('#order-form').on('submit', function(event) {
        $.ajax({
            data : {
                order : $('#order-input').val()
            },
            type : 'POST',
            url : '/process'
        })
        .done(function(data) {
            if(data) {
                $('#current-orders').text("").show();
                $('#orders-given').text('Orders: ' + data[0]["num_orders"] + '/' + data[0]["num_pieces"])
          
                for (var i = 1; i < data.length; i++) {
                    
                    // hold or disband
                    if (data[i].command == "hold" || data[i].command == "disband") {
                        $('#table-body').append('<tr><td>' + data[i].piece_type + " at " + data[i].territory + " will " + data[i].command + '</td></tr>').show();
                    }
                    // move or retreat
                    if (data[i].command == "move" || data[i].command == "retreat") {
                        $('#table-body').append('<tr><td>' + data[i].piece_type + " at " + data[i].territory + " will " + data[i].command + " to " + data[i].target + '</td></tr>').show();
                    }
                    // support or convoy
                    if (data[i].command == "support" || data[i].command == "convoy") {
                        $('#table-body').append('<tr><td>' + data[i].piece_type + " at " + data[i].territory + " will " + data[i].command + ' ' + data[i].object + " to " + data[i].target + '</td></tr>').show();
                    }
                }
            }
        });
        event.preventDefault();
    });
    $('#order-form').submit();
});
