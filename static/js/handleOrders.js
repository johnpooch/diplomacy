function sanitizeOrder(string) {
    var words = string.split(' ');
    console.log('AGGGH');
    // remove 'to', 'at', 'will', 'from'
    for (var i=words.length-1; i>=0; i--) {
        if (["to", "at", "will", "from"].indexOf(words[i]) > -1) {
            words.splice(i, 1);
        }
    }
    var cleanString = words.join(' ');
    return cleanString
}

$(document).ready(function() {
    $('#order-form').on('submit', function(event) {
        
        var orderSanitized = sanitizeOrder($('#order-input').val())
        
        $.ajax({
            data : {
                order : orderSanitized
            },
            type : 'POST',
            url : '/process'
        })
        .done(function(data) {
            if(data) {
                $('#order-input').val('');
                
                $('#create-order').css({"display": "block"});
                $('#order-form').css({"display": "none"});
                
                $('#table-body').text("").show();
                $('#orders-given').text('Orders: ' + data[0]["num_orders"] + '/' + data[0]["num_pieces"])
                
                console.log(data)
                
                if (data[0]["num_orders"] == data[0]["num_pieces"]) {
                    $('#create-order').css({"display": "none"});
                    $('#orders-issued').css({"display": "block"});
                }
                
                var random_id = function() {
                    var id_num = Math.random().toString(9).substr(2,3);
                    var id_str = Math.random().toString(36).substr(2);
                    return id_num + id_str;
                }
                
                // create order table
                var tbl = '';
                tbl +='<table id="table">';
                
                // table header
                tbl += '<thead>';
                    tbl += '<tr>';
                    tbl += '<th>Orders</th>';
                    tbl += '<th></th>';
                    tbl += '</tr>';
                tbl += '<thead>';
                
                // table body
                tbl +='<tbody>';
                
                    $.each(data.slice(1), function(index, val) {
                        var row_id = random_id();
                        var orderString = "";
                        
                        // orderStrings for different commands
                        if (val["command"] == "hold" || val.command == "disband") {
                            orderString = val["piece_type"] + " at " + val["territory"] + " will " + val["command"];
                        }
                        if (val["command"] == "move" || val.command == "retreat") {
                            orderString = val["piece_type"] + " at " + val["territory"] + " will " + val["command"] + ' to ' + val["target"];
                        }
                        if (val["command"] == "support" || val.command == "convoy") {
                            orderString = val["piece_type"] + " at " + val["territory"] + " will " + val["command"] + ' ' + val["object"] + ' to ' + val["target"];
                        }
                        
                        tbl += '<tr row_id="' + row_id + '">';
                        
                            // orders column
                            tbl += '<td><div class="row_data" edit_type="click" col_name="order" draggable="false")>' + orderString + '</div></td>';
                            
                            // options column
                            tbl += '<td>';
                                tbl += '<span class="btn_edit"><a href="#" class="btn btn-link" row_id="' + row_id + '"><i class="fa fa-edit"></i></a></span>';
                            tbl += '</td>';
                        tbl += '</tr>';
                    });
                tbl += '</tbody>'
                tbl += '</table>'
                  
                // output data
                $(document).find('#tbl_orders').html(tbl);
                
                // make inputs not draggable
                $(document).find('.row_data').mouseenter(function () {
                    $('#draggable').draggable({
                      disabled: true
                    });
                });
                $(document).find('.row_data').mouseleave(function () {
                    $('#draggable').draggable({
                      disabled: false
                    });
                });
                
                //--->button > edit > start	
                $(document).on('click', '.btn_edit', function(event) 
                {
                    $('#create-order').css({"display": "none"});
                    $('#order-form').css({"display": "block"}).focus();
                    
                    $('#order-input').val($(this).closest('tr').find('.row_data').text())
                
                	//--->add the original entry > end
                
                });
                //--->button > edit > end

            }
        });
        event.preventDefault();
    });
    $('#order-form').submit();
});
