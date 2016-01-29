var googleApiKey = 'AIzaSyABxbqtLTNxu3q9XkVCRCpvDP2F7N_xtww';

function starPhrase(phraseId) {
  var url = '/api/phrases/' + phraseId + '/star';
  fetch(url, {
    method: 'post',
    credentials: 'include',
    headers: {
      "X-CSRFToken": CSRF_TOKEN
    }
  }).catch(function(error) {
    console.log('Error: :-S', error);
  });
}

function unstarPhrase(phraseId) {
  var url = '/api/phrases/' + phraseId + '/star';
  fetch(url, {
    method: 'delete',
    credentials: 'include',
    headers: {
      "X-CSRFToken": CSRF_TOKEN
    }
  }).catch(function(error) {
    console.log('Error: :-S', error);
  });
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
