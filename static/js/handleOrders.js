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
                $('#order-input').val('');
                
                $('#create-order').css({"display": "block"});
                $('#order-form').css({"display": "none"});
                
                $('#table-body').text("").show();
                $('#orders-given').text('Orders: ' + data[0]["num_orders"] + '/' + data[0]["num_pieces"])
                
                console.log(data[0])
                
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
                            tbl += '<td><div class="row_data" edit_type="click" col_name="order" contenteditable="true" draggable="false")>' + orderString + '</div></td>';
                            
                            // options column
                            tbl += '<td>';
                                tbl += '<span class="btn_edit"><a href="#" class="btn btn-link" row_id="' + row_id + '"><i class="fa fa-edit"></i></a></span>';
                                tbl += '<span class="btn_save"><a href="#" class="btn btn-link" row_id="' + row_id + '">Save</a></span>';
                                tbl += '<span class="btn_cancel"><a href="#" class="btn btn-link" row_id="' + row_id + '">Cancel</a></span>';
                            tbl += '</td>';
                        tbl += '</tr>';
                    });
                tbl += '</tbody>'
                tbl += '</table>'
                  
                // output data
                $(document).find('#tbl_orders').html(tbl);
                
                // hide options
                $(document).find('.btn_save').hide();
                $(document).find('.btn_cancel').hide();
                
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
                	event.preventDefault();
                	var tbl_row = $(this).closest('tr');
                
                	var row_id = tbl_row.attr('row_id');
                
                	tbl_row.find('.row_data')
                	.css('padding', '5px')
                    .focus();

                	//--->add the original entry > end
                
                });
                //--->button > edit > end

            }
        });
        event.preventDefault();
    });
    $('#order-form').submit();
});
