
var example = "example orders: 'army at bre move to eng', 'fleet at mid support eng to bre'";
var numberPresent = "orders should not include numbers.";
var notPieceType = "orders must begin with the type of the piece you wish to order (i.e. army, fleet).";
var notTerritory = "you must enter a valid territory abbreviation.";
var notCommand = "you must give a valid command ('hold', 'move', 'support', 'convoy')";
var tooManyHoldWords = "hold order has too many words (ex. 'army ven hold')";
var tooManyMoveWords = "move order has too many words (ex. 'army tri move vie')";
var tooManySupportWords = "support order has too many words (ex. 'army tri support vie ven')";
var validOrder = "Order is valid";

var pieceTypes = ["army", "fleet"];
var commands = ["hold", "move", "support", "convoy"];
var territories = ['adr','aeg','bal','bar','bla','bot','eas','eng','gol','hel','ion','iri','mid','nat','nrg','nth','ska','tyn','wes','alb','ank','apu','arm','ber','bel','bre','cly','con','den','edi','fin','gas','gre','hol','kie','lon','lvn','lvp','mar','naf','nap','nwy','pic','pie','por','rom','rum','pru','sev','smy','swe','syr','tri','tun','tus','ven','wal','yor','boh','bud','bur','gal','mos','mun','par','ruh','ser','sil','tyr','ukr','vie','war','bul','spa','stp','bul_ec','bul_sc','spa_nc','spa_sc','stp_sc','stp_nc'];

function hasNumber(myString) {
  return /\d/.test(myString);
}

function wordInPieceTypes(word) {
  return (pieceTypes.indexOf(word) > -1);
}
function wordInCommands(word) {
  return (commands.indexOf(word) > -1);
}
function wordInTerritories(word) {
  return (territories.indexOf(word) > -1);
}

function preventEnter(event){
  if (event.which == '13') {
    event.preventDefault();
  }
}

$('.order-input').after('<div id="feedback" class="feedback">' + example + '</div>')

$( ".order-input" ).focus(function() {
  $(this).next().css("color", "black");
});
$( ".order-input" ).blur(function() {
  $(this).next().css("color", "transparent");
});

$('.order-input').on('input', function (evt) {
  var value = evt.target.value.toLowerCase()
  var words = value.split(" ")
  
  function sanitizeOrder(words) {
    // remove 'to', 'at', 'will', 'from'
    for (var i=words.length-1; i>=0; i--) {
      if (["to", "at", "will", "from"].indexOf(words[i]) > -1) {
          words.splice(i, 1);
      }
    }
  }
  sanitizeOrder(words);

  // this appears unless any other condition is met
  $('#feedback').text(example)
  preventEnter(event);
  evt.target.className = ''
  
  // check first word
  if (words.length > 1) {
    if (!wordInPieceTypes(words[0])) {
      console.log('first word is not a piece type')
      $('#feedback').text(notPieceType);
      preventEnter(event); 
      evt.target.className = 'invalid';
    }
  }
    
  // check second word
  if (words.length > 2) {
    if (!wordInTerritories(words[1])) {
      console.log('second word is not a valid territory')
      $('#feedback').text(notTerritory);
      preventEnter(event);
      evt.target.className = 'invalid';
    }
  }
  
  // check third word
  if (words.length > 3) {
    if (!wordInCommands(words[2])) {
      console.log('third word is not a valid command')
      $('#feedback').text(notCommand);
      preventEnter(event);
      evt.target.className = 'invalid';
    }
  }
  
  // check fourth word
  if (words.length > 4) {
    if (!wordInTerritories(words[3])) {
      console.log('fourth word is not a valid territory')
      $('#feedback').text(notTerritory);
      preventEnter(event);
      evt.target.className = 'invalid';
    }
  }
  
  // check fifth word
  if (words.length > 5) {
    if (!wordInTerritories(words[4])) {
      console.log('fifth word is not a valid territory')
      $('#feedback').text(notTerritory);
      preventEnter(event);
      evt.target.className = 'invalid';
    }
  }
  
  // if number present
  if (hasNumber(value)) {
    $('#feedback').text(numberPresent);
    preventEnter(event);
    evt.target.className = 'invalid';
  }
  
  // hold
  if (words[2] == 'hold') {
    if(words.length > 3) {
      console.log('command is hold but too many words given')
      $('#feedback').text(tooManyHoldWords);
      preventEnter(event);
      evt.target.className = 'invalid';
    }
    else if (words.length == 3) {
      console.log('valid hold command')
      $('#feedback').text("hold order is valid - press enter to issue order");
      evt.target.className = 'valid';
    }
  }
  
  // move
  if (words[2] == 'move') {
    if(words.length > 4) {
      console.log('command is move but too many words given')
      $('#feedback').text(tooManyMoveWords);
      preventEnter(event);
      evt.target.className = 'invalid';
    }
    else if (words.length == 4 && wordInTerritories(words[3])) {
      console.log('valid move command')
      $('#feedback').text("move order is valid - press enter to issue order");
      evt.target.className = 'valid';
    }
  }
  // support
  if (words[2] == 'support') {
    if(words.length > 5) {
      console.log('command is support but too many words given')
      $('#feedback').text(tooManySupportWords);
      preventEnter(event);
      evt.target.className = 'invalid';
    }
    else if (words.length == 5 && wordInTerritories(words[3]) && wordInTerritories(words[4])) {
      console.log('valid move command')
      $('#feedback').text("support order is valid - press enter to issue order");
      evt.target.className = 'valid';
    }
  }
  
  // convoy
  if (words[2] == 'convoy') {
    if(words.length > 5) {
      console.log('command is convoy but too many words given')
      $('#feedback').text(tooManySupportWords);
      preventEnter(event);
      evt.target.className = 'invalid';
    }
    else if (words.length == 5 && wordInTerritories(words[3]) && wordInTerritories(words[4])) {
      console.log('valid move command')
      $('#feedback').text("convy order is valid - press enter to issue order");
      evt.target.className = 'valid';
    }
  }

});