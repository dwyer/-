'use strict';

(function () {

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
                       + ' zh-phrase-id-' + phrase.id + '">' + phrase.phrase
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


  .directive('zhGet', ['$compile', function ($compile) {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        element.html(scope.$parent.vars[attrs.zhGet]);
      }
    };
  }])


  .directive('zhSet', ['$compile', function ($compile) {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        if (!scope.$parent.vars)
          scope.$parent.vars = {};
        scope.$parent.vars[attrs.zhSet] = element.html();
      }
    };
  }])


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


  .filter('embeddedVideoUrl', ['$sce', function ($sce) {
    var p = /^https?:\/\/www\.youtube\.com\/watch\?v=(\w+)$/;
    return function (input) {
      var m = p.exec(input);
      if (m) {
        return $sce.trustAsResourceUrl('https://www.youtube.com/embed/' + m[1]);
      }
      return null;
    };
  }])


  .filter('processText', ['$sce', function ($sce) {
    return processText;
    return function (input) {
      return $sce.trustAsHtml(processText(input));
    };
  }])


  .controller('TextListCtrl', ['$scope', '$http', function ($scope, $http) {
    $http.get(API_BASE_URL + 'texts?fields=id,title,video_url')
    .then(function (response) {
      $scope.texts = response.data.results;
    });
  }])


  .controller('TextDetailCtrl', [
    '$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
      $scope.data = {};
      $scope.editMode = false;
      $scope.selection = null;

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

      $scope.changePhraseLevel = function () {
        var phrase = $scope.selectedPhrase;
        $http.put(API_BASE_URL + 'phrases/' + phrase.id, phrase)
        .then(function (response) {
          updateProgressBar();
        });
      };

      $scope.selectTerm = function (selection) {
        var oldSelection = $scope.selection;
        $scope.selection = selection;
        if ($scope.selection.length > 0 && $scope.selection !== oldSelection) {
          $http.get(API_BASE_URL + 'terms?traditional='
                    + encodeURIComponent($scope.selection))
          .then(function (response) {
            $scope.terms = response.data.results;
          });
          for (var i in $scope.text.phrases) {
            if ($scope.text.phrases[i].phrase == $scope.selection) {
              $scope.selectedPhrase = $scope.text.phrases[i];
              break;
            }
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

      $scope.save = function () {
        $scope.editMode = false;
        // $scope.text.text = $scope.data.processedText;
        $http.put(API_BASE_URL + 'texts/' + $routeParams.id, $scope.text)
        .then(function (response) {
          $scope.text = response.data;
          // $scope.data.processedText = processText($scope.text);
        });
      };

      $http.get(API_BASE_URL + 'texts/' + $routeParams.id)
      .then(function (response) {
        $scope.text = response.data;
        updateProgressBar();
        // $scope.data.processedText = processText($scope.text);
        $scope.isWritable = $scope.text.owner.id == USER_ID;
      });
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
        if (level > 4)
          level = 4;
        $scope.phrase.level = level;
        $http.put(API_BASE_URL + 'phrases/' + $scope.phrase.id, $scope.phrase);
        $scope.phrase = $scope.data.results.pop();
        $scope.terms = null;
      };

      load(API_BASE_URL + 'phrases?due=true');
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
