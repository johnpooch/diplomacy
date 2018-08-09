
var orderString = "";

// Parse Order String =============================================================================

function parseOrderString(string) {
    var words = string.split(' ');
    for (var i=words.length-1; i>=0; i--) { 
        if (["to", "at", "will", "from"].indexOf(words[i]) > -1) {
            words.splice(i, 1);
        }
    }
    return words.join(' ');
}

// ================================================================================================



// Input Not Draggable ============================================================================

function inputNotDraggable() {
    var row = $(document).find('.row-data');
    row.mouseenter(function () {
        $('#draggable').draggable({
          disabled: true
        });
    });
    row.mouseleave(function () {
        $('#draggable').draggable({
          disabled: false
        });
    });
}
// ================================================================================================



// Rows Editable ==================================================================================

function rowsEditable() {
    $(document).on('click', '.btn-edit', function(event) {
        $('#create-order').css({"display": "none"});
        $('#order-form').css({"display": "block"}).focus();
        
        $('#order-input').val($(this).closest('tr').find('.row-data').text());
    });
}

// ================================================================================================



// Reset Order Form ===============================================================================

function resetOrderForm(data) {
    // clear input field
    $('#order-input').val('');
    
    // hide input field
    $('#order-form').css({"display": "none"});
    
    // hide create order button if player has reached number of orders
    if (data[0]["num_orders"] == data[0]["num_pieces"]) {
        $('#create-order').css({"display": "none"});
    }
    else {
        $('#create-order').css({"display": "block"});
    }
    // show num orders given and num orders to give
    $('#orders-given').text('Orders: ' + data[0]["num_orders"] + '/' + data[0]["num_pieces"])
}

// ================================================================================================



// Create Random Id ===============================================================================

function createRandomId() {
    var id_num = Math.random().toString(9).substr(2,3);
    var id_str = Math.random().toString(36).substr(2);
    return id_num + id_str;
}

// ================================================================================================



// Get Order String ===============================================================================

function getOrderString(val) {
    if (val["command"] == "hold" || val["command"] == "disband") {
        orderString = val["piece_type"] + " at " + val["territory"] + " will " + val["command"];
    }
    if (val["command"] == "move" || val.command == "retreat") {
        orderString = val["piece_type"] + " at " + val["territory"] + " will " + val["command"] + ' to ' + val["target"];
    }
    if (val["command"] == "support" || val.command == "convoy") {
        orderString = val["piece_type"] + " at " + val["territory"] + " will " + val["command"] + ' ' + val["object"] + ' to ' + val["target"];
    }
    return orderString;
}

// ================================================================================================



// Create Table ===================================================================================

function createTable(data) {
    var tableHeader = '<table id="table"><thead><tr><th>Orders</th><th id="num-orders">' + data[0]["num_orders"] + '/' + data[0]["num_pieces"] + '</th></tr></thead>';
    
    var tableBody = '<tbody>'
    
    $.each(data.slice(1), function(index, val) {
        
        orderString = getOrderString(val);
        var row_id = createRandomId();
            
        tableBody += '<tr row_id="' + row_id + '">';
        tableBody += '<td><div class="row-data" edit_type="click" col_name="order" draggable="false")>' + orderString + '</div></td>';
        tableBody += '<td><span class="btn-edit"><a href="#" class="btn btn-link" row_id="' + row_id + '"><i class="fa fa-edit"></i></a></span></td></tr>';
    });
    tableBody += '</tbody>'
    tableBody += '</table>'
    return tableHeader + tableBody
}
// ================================================================================================



// Submit Order ===================================================================================

$(document).ready(function() {
    
    // send order to run.py -----------------------------------------------------------------------
    
    $('#order-form').on('submit', function(event) { 
        $.ajax({
            data : {
                order : parseOrderString($('#order-input').val())
            },
            type : 'POST',
            url : '/process'
        })
        
        // ----------------------------------------------------------------------------------------
        
        
        // receive data from run.py ---------------------------------------------------------------
        
        .done(function(data) {
            if(data) {
                resetOrderForm(data)
                
                $(document).find('#tbl_orders').html(createTable(data));
                
                inputNotDraggable();
                rowsEditable();
            }
        });
        event.preventDefault();
    });
    $('#order-form').submit();
});

// ================================================================================================