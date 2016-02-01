var googleApiKey = 'AIzaSyABxbqtLTNxu3q9XkVCRCpvDP2F7N_xtww';

function toggleStar(elem, phraseId) {
  var oldClassName = elem.className;
  var method = null;
  if (elem.className == 'glyphicon glyphicon-star') {
    elem.className = 'glyphicon glyphicon-star-empty';
    method = 'delete';
  } else if (elem.className == 'glyphicon glyphicon-star-empty') {
    elem.className = 'glyphicon glyphicon-star';
    method = 'post';
  }
  if (method !== null) {
    fetch('/api/v1/phrases/' + phraseId + '/star', {
      method: method,
      credentials: 'include',
      headers: {
        "X-CSRFToken": CSRF_TOKEN
      }
    }).catch(function(error) {
      elem.className = oldClassName;
      console.log('Error: :-S', error);
    });
  }
}

function googleTranslate(id, phrase, source, target) {
  var url = 'https://www.googleapis.com/language/translate/v2' + '?key=' + googleApiKey + '&q=' + phrase + '&source=' + source + '&target=' + target;
  fetch(url).then(function(response) {
    if (response.status !== 200) {
      console.log('Error: Status Code: ', response.status);
      return;
    }
    response.json().then(function(data) {
      var translations = data.data.translations;
      for (var i = 0; i < translations.length; i++) {
        var elem = document.getElementById(id);
        console.log(i, translations[i].translatedText);
        elem.innerHTML = translations[i].translatedText;
      }
    });
  }).catch(function(error) {
    console.log('Error: :-S', error);
  });
}

function textSelectListener(event) {
  var selection = document.getSelection();
  var string = selection.toString();
  if (string.length > 0) {
    fetch('/api/v1/phrases?traditional=' + encodeURIComponent(string)).then(function(response) {
      if (response.status == 200) {
        response.json().then(function (data) {
          for (var i in data.results) {
            var result = data.results[i];
            console.log('T: ' + result.traditional);
            console.log('S: ' + result.simplified);
            console.log('P: ' + result.pinyin);
            for (var j in result.translations) {
              console.log('- ' + result.translations[j].translation);
            }
          }
        });
      }
    }).catch(function(error) {
      console.log('Error: :-S', error);
    });
  }
}
