$(document).ready(function() {
  var socket = io.connect('http://diplomacy-johnpooch.c9users.io:8080/');
  socket.on('message', function(message) {
    $("#messages li:eq(0)").before("<li><div class='row'>"+ message + "</div></li><hr>");
    $("#messages li:eq(0)").before("<li><div class='row'><strong>{{user['nation']|capitalize}}<strong></div></li>");
  })
  $('#sendButton').on('click', function() {
    socket.send("{{ user['nation'] }} - " + $('#myMessage').val());
    $('#myMessage').val('');
  })
});