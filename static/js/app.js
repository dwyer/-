'use strict';

(function () {

  function objectUpdate(a, b) {
      angular.forEach(Object.keys(b), function (key) {
        if (!key.startsWith('$'))
          a[key] = b[key];
      });
  };

  function playAudio(text) {
    var url = API_BASE_URL + 'audio/' + text + '.mp4';
    var audio = new Audio(url);
    audio.play();
  }

  function processText(text) {
    text.phrases.sort(function (a, b) {
      return b.phrase.length - a.phrase.length;
    });
    var map = {};
    for (var i in text.phrases) {
      var phrase = text.phrases[i];
      var key = phrase.phrase[0];
      if (map[key] === undefined) {
        map[key] = [];
      }
      map[key].push(i);
    }
    var fragments = [];
    var s = text.text;
    while (s.length) {
      var phrase = null;
      var index = -1;
      var key = s[0];
      if (map[key] !== undefined) {
        for (var j in map[key]) {
          index = map[key][j];
          phrase = text.phrases[index];
          if (phrase.phrase == s.substring(0, phrase.phrase.length)) {
            break;
          }
        }
      }
      if (phrase === null) {
        fragments.push(s[0]);
        s = s.substring(1);
      } else {
        fragments.push('<span class="zh-phrase zh-phrase-' + phrase.level
                       + ' zh-phrase-id-' + phrase.phrase + '">' + phrase.phrase
                       + '</span>');
        s = s.substring(phrase.phrase.length);
      }
    }
    return fragments.join('');
  }

  angular.module('yanjiu', [
    'ngMessageFormat',
    'ngRoute',
    'ngSanitize',
    'mgcrea.ngStrap.affix',
    'mgcrea.ngStrap.dropdown',
    'mgcrea.ngStrap.tooltip',
  ])


  .config(['$httpProvider', function ($httpProvider) {
    $httpProvider.defaults.headers.common['X-CSRFToken'] = CSRF_TOKEN;
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
  }])


  .config(['$routeProvider', function ($routeProvider) {
    $routeProvider
    .when('/texts', {
      templateUrl: PARTIALS_DIR + 'text_list.html',
      controller: 'TextListCtrl'//,
    })
    .when('/texts/create', {
      templateUrl: PARTIALS_DIR + 'text_edit.html',
      controller: 'TextCreateCtrl'//,
    })
    .when('/texts/:id', {
      templateUrl: PARTIALS_DIR + 'text_detail.html',
      controller: 'TextDetailCtrl'//,
    })
    .when('/texts/:id/edit', {
      templateUrl: PARTIALS_DIR + 'text_edit.html',
      controller: 'TextEditCtrl'//,
    })
    .when('/phrases', {
      templateUrl: PARTIALS_DIR + 'phrase_list.html',
      controller: 'PhraseListCtrl'//,
    })
    .when('/flashcards', {
      templateUrl: PARTIALS_DIR + 'flashcards.html',
      controller: 'FlashCardsCtrl'//,
    })
    .when('/search/:lang/:query', {
      templateUrl: PARTIALS_DIR + 'search.html',
      controller: 'SearchCtrl'//,
    })
    .when('/terms/starred', {
      templateUrl: PARTIALS_DIR + 'search.html',
      controller: 'StarredTermsCtrl'//,
    })
    .otherwise({redirectTo: '/'});
  }])


  .run(['$rootScope', '$http', function ($rootScope, $http) {
    $rootScope.userId = USER_ID;
    $rootScope.partialsUrl = PARTIALS_DIR;
    $rootScope.playAudio = playAudio;

    $rootScope.toggleStar = function (term) {
      var url = API_BASE_URL + 'terms/' + term.id + '/star';
      if (!term.is_starred) {
        $http.post(url).then(function (response) {
          //
        });
      } else {
        $http.delete(url).then(function (response) {
          //
        });
      }
      term.is_starred = !term.is_starred;
    };
  }])


  .directive('zhGet', function () {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        element.html(scope.$parent.vars[attrs.zhGet]);
      }
    };
  })


  .directive('zhSet', function () {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        if (!scope.$parent.vars)
          scope.$parent.vars = {};
        scope.$parent.vars[attrs.zhSet] = element.html();
      }
    };
  })


  .directive('zhText', ['$compile', function ($compile) {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        scope.$watch(function (scope) {
          return scope.$eval(attrs.zhText);
        }, function (value) {
          element.html(value);
          $compile(element.contents())(scope);
        });
      }
    };
  }])


  .directive('zhPhrase', function () {
    return {
      restrict: 'A',
      scope: {zhPhrase: '='},
      link: function (scope, element, attrs) {
        element.html(scope.zhPhrase.phrase);
        element.addClass('zh-phrase');
        element.addClass('zh-phrase-' + scope.zhPhrase.level);
      }
    };
  })


  .directive('contenteditable', ['$sce', function ($sce) {
    return {
      restrict: 'A',
      require: '?ngModel',
      link: function (scope, element, attrs, ngModel) {
        if (!ngModel)
          return;
        ngModel.$render = function () {
          element.html(ngModel.$viewValue || '');
        };
        function read() {
          ngModel.$setViewValue(element.html());
        }
        element.bind('blur keyup change', function () {
          scope.$evalAsync(read);
        });
      }
    };
  }])


  .filter('embeddedVideoUrl', function () {
    var p = /^https?:\/\/www\.youtube\.com\/watch\?v=([-_\w]+)$/;
    return function (input) {
      var m = p.exec(input);
      if (m) {
        return 'https://www.youtube.com/embed/' + m[1];
      }
      return null;
    };
  })


  .filter('processText', ['$sce', function ($sce) {
    return processText;
    return function (input) {
      return $sce.trustAsHtml(processText(input));
    };
  }])


  .filter('timedelta', function () {
    var lst = [
      {seconds: 60 * 60 * 24, type: 'day'},
      {seconds: 60 * 60, type: 'hour'},
      {seconds: 60, type: 'minute'},
    ];
    return function (input) {
      if (!input)
        return 'never';
      var units = (new Date() - new Date(input)) / 1000;
      var isPast = units >= 0;
      var type = 'second';
      units = Math.abs(units);
      for (var i in lst) {
        if (units >= lst[i].seconds) {
          units /= lst[i].seconds;
          type = lst[i].type;
          break;
        }
      }
      units = Math.floor(units);
      var string =  units + ' ' + type;
      if (units != 1)
        string = string + 's';
      if (isPast)
        string = string + ' ago';
      else
        string = 'in ' + string;
      return string;
    };
  })


  .filter('translation', function ($sce) {
    var pattern = /([一-龥|]+)\[([\w\s\d]+)\]/;
    return function (input) {
      var match = pattern.exec(input);
      if (match) {
        var term = match[1].split('|')[0];
        var url = '#/search/zh-tw/' + encodeURIComponent(term);
        var tag = '<a href="' + url + '">' + term + '</a>';
        input = input.replace(match[0], tag);
      }
      return input;
    };
  })


  .filter('truncate', ['$sce', function ($sce) {
    var ellipsis = '...';
    return function (input, length) {
      if (!length)
        length = 100;
      if (input.length > length)
        input = input.substring(0, length - ellipsis.length) + ellipsis;
      return $sce.trustAsHtml(input);
    };
  }])


  .filter('trustAsResourceUrl', ['$sce', function ($sce) {
    return $sce.trustAsResourceUrl;
  }])


  .controller('TextListCtrl', ['$scope', '$http', function ($scope, $http) {

    $scope.load = function (url) {
      $http.get(url).then(function (response) {
        if (!url)
          return;
        $scope.data = response.data;
        $scope.texts = response.data.results;
      });
    };

    $scope.load(API_BASE_URL + 'texts?fields=id,title,audio_url,video_url,updated&order=title');

  }])


  .controller('TextDetailCtrl', [
    '$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
      $scope.data = {};
      $scope.editMode = false;
      $scope.selection = null;

      $scope.load = function () {
        $http.get(API_BASE_URL + 'texts/' + $routeParams.id)
        .then(function (response) {
          $scope.text = response.data;
          updateProgressBar();
          // $scope.data.processedText = processText($scope.text);
          $scope.isWritable = $scope.text.owner.id == USER_ID;
        });
      }

      function updateProgressBar() {
        var progress = [0, 0, 0, 0, 0, 0];
        for (var i in $scope.text.phrases) {
          progress[$scope.text.phrases[i].level] += 1;
        }
        for (var i in progress) {
          progress[i] /= $scope.text.phrases.length;
          progress[i] *= 100;
        }
        $scope.progress = progress;
      }

      $scope.selectTerm = function (selection) {
        var oldSelection = $scope.selection;
        $scope.selection = selection;
        if ($scope.selection.length > 0 && $scope.selection !== oldSelection) {
          $http.get(API_BASE_URL + 'terms?traditional='
                    + encodeURIComponent($scope.selection))
          .then(function (response) {
            $scope.terms = response.data.results;
          });
          $scope.phrase = null;
          for (var i in $scope.text.phrases) {
            if ($scope.text.phrases[i].phrase == $scope.selection) {
              $scope.phrase = $scope.text.phrases[i];
              break;
            }
          }
          if (!$scope.phrase) {
            $http.get(API_BASE_URL + 'phrases/' + $scope.selection)
            .then(function (response) {
              $scope.phrase = response.data;
            });
          }
        }
      };

      $scope.listener = function () {
        $scope.selectTerm(window.getSelection().toString());
      };

      $scope.toggleEditMode = function () {
        // $scope.data.processedText = processText($scope.text);
        $scope.editMode = !$scope.editMode;
      };

      $scope.toggleVideo = function () {
        $scope.showVideo = !$scope.showVideo;
      };

      $scope.save = function () {
        $scope.editMode = false;
        // $scope.text.text = $scope.data.processedText;
        $http.put(API_BASE_URL + 'texts/' + $routeParams.id, $scope.text)
        .then(function (response) {
          $scope.text = response.data;
          // $scope.data.processedText = processText($scope.text);
        });
      };

      $scope.load();
    }
  ])


  .controller('TextEditCtrl', [
    '$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {

      $scope.finish = function () {
        window.location.href = '#/texts/' + $routeParams.id;
      };

      $scope.submit = function (isValid, finish) {
        if (isValid) {
          $http.put(API_BASE_URL + 'texts/' + $routeParams.id, $scope.text)
          .then(function (response) {
            if (finish)
              $scope.finish();
            else
              $scope.text = response.data;
          }, function (response) {
            $scope.error = response.data;
          });
        }
      };

      $http.get(API_BASE_URL + 'texts/' + $routeParams.id)
      .then(function (response) {
        $scope.text = response.data;
        if ($scope.text.owner.id != USER_ID) {
          // TODO: raise error
        }
      });
    }
  ])


  .controller('TextCreateCtrl', [
    '$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
      $scope.text = {};

      $scope.finish = function () {
        if (window.history.length > 1)
          window.history.back();
        else
          window.location.href = '#/';
      };

      $scope.submit = function (isValid) {
        if (isValid) {
          $http.post(API_BASE_URL + 'texts', $scope.text)
          .then(function (response) {
            window.location.href = '#/texts/' + response.data.id;
          }, function (response) {
            $scope.error = response.data;
          });
        }
      };
    }
  ])


  .controller('PhraseListCtrl', [
    '$scope', '$http',
    function ($scope, $http) {

      $scope.lookup = function (phrase) {
        var term = phrase.phrase;
        $scope.phrase = phrase;
        $http.get(API_BASE_URL + 'terms?traditional=' + encodeURIComponent(term))
        .then(function (response) {
          $scope.terms = response.data.results;
        });
      };

      $scope.edit = function (phrase) {
        $http.put(API_BASE_URL + 'phrases/' + phrase.phrase, phrase)
        .then(function (response) {
          objectUpdate(phrase, response.data);
        });
      };

      $scope.load = function (url) {
        $http.get(url).then(function (response) {
          $scope.data = response.data;
          $scope.phrases = response.data.results;
        });
      };

      $scope.load(API_BASE_URL + 'phrases?order=-updated');

    }
  ])


  .controller('PhraseDetailCtrl', ['$scope', '$http', function ($scope, $http) {
      $scope.updatePhrase = function (phrase) {
        var promise = null;
        if (phrase.updated)
          promise = $http.put(API_BASE_URL + 'phrases/' + phrase.phrase, phrase);
        else
          promise = $http.post(API_BASE_URL + 'phrases', phrase);
        promise.then(function (response) {
          objectUpdate(phrase, response.data);
          updateProgressBar();
        });
      };
  }])


  .controller('FlashCardsCtrl', [
    '$scope', '$http',
    function ($scope, $http) {

      function load(url) {
        $http.get(url).then(function (response) {
          $scope.data = response.data;
          $scope.phrase = $scope.data.results.pop();
        });
      }

      $scope.show = function () {
        playAudio($scope.phrase.phrase);
        $http.get(API_BASE_URL + 'terms?traditional='
                  + encodeURIComponent($scope.phrase.phrase))
        .then(function (response) {
          $scope.terms = response.data.results;
        });
      };

      $scope.setLevel = function (level) {
        if (level < 1)
          level = 1;
        if (level > 5)
          level = 5;
        $scope.phrase.level = level;
        $http.put(API_BASE_URL + 'phrases/' + $scope.phrase.phrase, $scope.phrase);
        $scope.phrase = $scope.data.results.pop();
        $scope.terms = null;
      };

      load(API_BASE_URL + 'phrases?due=true&random=true');
    }])


  .controller('SearchCtrl', [
    '$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
      $scope.terms = {};
      $scope.search_query = $routeParams.query;

      $scope.more = function () {
        $http.get($scope.data.next).then(function (response) {
          $scope.data = response.data;
          for (var i in response.data.results)
            $scope.terms.push(response.data.results[i]);
        });
      }

      $http.get(API_BASE_URL + 'terms?q='
                + encodeURIComponent($routeParams.query) + '&lang='
                + encodeURIComponent($routeParams.lang))
                .then(function (response) {
                  $scope.data = response.data;
                  $scope.terms = response.data.results;
                });
    }
  ])


  .controller('StarredTermsCtrl', ['$scope', '$http', function ($scope, $http) {
    $scope.terms = {};

    $scope.more = function () {
      $http.get($scope.data.next).then(function (response) {
        $scope.data = response.data;
        for (var i in response.data.results)
          $scope.terms.push(response.data.results[i]);
      });
    }

    $http.get(API_BASE_URL + 'terms?starred=true')
    .then(function (response) {
      $scope.data = response.data;
      $scope.terms = response.data.results;
    });
  }
  ])


  .controller('SearchFormCtrl', ['$scope', function ($scope) {
    $scope.lang = 'zh-tw';

    $scope.search = function () {
      window.location.href = ('#/search/' + encodeURIComponent($scope.lang)
                              + '/' + encodeURIComponent($scope.query));
    };
  }]);

})();
