
var orderString = "";

// Parse Order String =============================================================================

/* The user's input is stripped of certain non-essential words. This means that and order like 'army ven
    move to par' would be the same as 'army ven move par'. */

function parseOrderString(string) {
    var words = string.split(' ');
    for (var i=words.length-1; i>=0; i--) { 
        if (["to", "at", "will", "from", "in"].indexOf(words[i]) > -1) {
            words.splice(i, 1);
        }
    }
    return words.join(' ');
}

// ================================================================================================



// Input Not Draggable ============================================================================

/* This function makes the ui modal non-draggable when the cursor is in the input field. This means 
    user's can drag over text to edit orders without moving the ui modal accidentally. */

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



// Reset Order Form ===============================================================================

/* This function restores the order form to the appropriate state after an order is given. When the 
    user has given all available orders the 'create order' button is hidden. */

function resetOrderForm(data) {
    
    $('#order-input').val('');
    $('#order-form').css({"display": "none"});
    
    // hide create order button if player has reached number of orders
    if (data[0]["orders_submitted"] == data[0]["num_orders"]) {
        $('#create-order').css({"display": "none"});
    }
    else {
        $('#create-order').css({"display": "block"});
    }
    // show num orders given and num orders to give
    $('#orders-given').text('Orders: ' + data[0]["orders_submitted"] + '/' + data[0]["num_orders"])
}

// ================================================================================================



// Get Order String ===============================================================================

/* When displaying the orders back to the user, a slightly different syntax is used depending on the command. */
// Orders could have an order string as a property which would mean that this logic could be handled on the back end.

function getOrderString(val) {
    if (val["command"] == "build") {
        orderString = val["command"] + ' ' + val["piece_type"] + " at " + val["territory"];
    }
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

/* Creates a table of the user's orders. The delete button is also created as part of the table. */

function createTable(data) {
    
    var tableHeader = '<table id="table"><thead><tr><th>Orders</th><th id="num-orders">' + data[0]["orders_submitted"] + '/' + data[0]["num_orders"] + '</th></tr></thead>';
    var tableBody = '<tbody>';
    
    $.each(data.slice(1), function(index, val) {
        
        orderString = getOrderString(val);
        var row_id = val["id"];
            
        tableBody += '<tr row_id="' + row_id + '" class = order-row>';
        tableBody += '<td><div class="row-data" edit_type="click" col_name="order" draggable="false")>' + orderString + '</div></td>';
        tableBody += '<td><span class="btn-delete"><a href="#" class="btn btn-link delete" row_id="' + row_id + '"><i class="fa fa-minus"></i></a></span></td></tr>';
    });
    tableBody += '</tbody>';
    tableBody += '</table>';
    return tableHeader + tableBody;
}
// ================================================================================================



// Submit Order ===================================================================================

/* Orders are submitted to the run.py script using ajax. The mongo db is then updated and all of the user's orders
    are returned and displyed in a table. */

$(document).ready(function() {
    
    // send order to run.py -----------------------------------------------------------------------
    
    $('#order-form').on('submit', function(event) { 
        $.ajax({
            data : {
                order : parseOrderString($('#order-input').val()), 
            },
            type : 'POST',
            url : '/process'
        })
        
        // receive data from run.py ---------------------------------------------------------------
        
        .done(function(data) {
            console.log(data)
            if (data == "all orders submitted") {
                window.location.href = "/"
                console.log("should referesh?")
            }
            else if(data) {
                resetOrderForm(data)
                $(document).find('#tbl_orders').html(createTable(data));
                inputNotDraggable();
            }
        });
        event.preventDefault();
    });
    $('#order-form').submit();
});

// ================================================================================================



// Delete Order ===================================================================================

$(document).ready(function() {
    
    // send order to run.py -----------------------------------------------------------------------
    
    $(document).on('click', '.delete', function(event) {
        
        $.ajax({
            data : {
                id : $(this).closest('.order-row').attr("row_id")
            },
            type : 'POST',
            url : '/process'
        })
        
        // receive data from run.py ---------------------------------------------------------------
        .done(function(data) {
            if(data) {
                resetOrderForm(data)
                $(document).find('#tbl_orders').html(createTable(data));
                inputNotDraggable();
            }
        });
        event.preventDefault();
    });
});

// ================================================================================================
