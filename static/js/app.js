'use strict';

(function () {

  var app = angular.module('yanjiu', [
    'ngMessageFormat',
    'ngRoute',
    'ngSanitize',
    'mgcrea.ngStrap.affix',
  ]);


  app.config(['$httpProvider', function ($httpProvider) {
    $httpProvider.defaults.headers.common['X-CSRFToken'] = CSRF_TOKEN;
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
  }]);


  app.config(['$routeProvider', function ($routeProvider) {
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
    .when('/search/:lang/:query', {
      templateUrl: PARTIALS_DIR + 'search.html',
      controller: 'SearchCtrl'//,
    })
    .when('/phrases/starred', {
      templateUrl: PARTIALS_DIR + 'search.html',
      controller: 'StarredPhrasesCtrl'//,
    })
    .otherwise({redirectTo: '/'});
  }]);


  app.factory('phraseService', ['$http', function ($http) {
    return {
      playAudio: function (phrase) {
        var url = '/audio/' + phrase + '.mp4';
        var audio = new Audio(url);
        audio.play();
      }
    };
  }]);


  app.directive('contenteditable', ['$sce', function ($sce) {
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
  }]);


  app.filter('embeddedVideoUrl', ['$sce', function ($sce) {
    var p = /^https?:\/\/www\.youtube\.com\/watch\?v=(\w+)$/;
    return function (input) {
      var m = p.exec(input);
      if (m) {
        return $sce.trustAsResourceUrl('https://www.youtube.com/embed/' + m[1]);
      }
      return null;
    };
  }]);


  /**
   * Wrap Chinese sentences in a span.zh-sent tag.
   * TODO: lookup words.
   */
  app.filter('processText', ['$sce', function ($sce) {

    var cache = {};

    function lookup(phrase) {
      if (cache.html) {

      }
    }

    function parseSentence(sent) {
      return [sent];
    }

    return function (input) {
      // input = $sanitize(input);
      var fragments = [];
      var pattern = /[一-龥]+/;
      while (input.length) {
        var match = pattern.exec(input);
        if (!match) {
          if (input.length) {
            fragments.push(input);
          }
          break;
        }
        if (match.index > 0) {
          fragments.push(input.substring(0, match.index));
        }
        fragments.push('<span class="zh-sent">');
        fragments.push(match[0]);
        fragments.push('</span>');
        input = input.substring(match.index + match[0].length);
      }
      return $sce.trustAsHtml(fragments.join(''));
    };
  }]);


  app.controller('TextListCtrl', ['$scope', '$http', function ($scope, $http) {
    $http.get('/api/v1/texts?fields=id,title,video_url')
    .then(function (response) {
      $scope.texts = response.data.results;
    });
  }]);


  app.controller('TextDetailCtrl', [
    '$scope', '$http', '$routeParams', 'phraseService',
    function ($scope, $http, $routeParams, phraseService) {
      $scope.phraseService = phraseService;
      $scope.data = {};
      $http.get('/api/v1/texts/' + $routeParams.id)
      .then(function (response) {
        $scope.text = response.data;
        $scope.data.processedText = $scope.text.processed_text;
        $scope.isWritable = $scope.text.owner.id == USER_ID;
      });
      $scope.phraseListPartialUrl = PARTIALS_DIR + 'phrase_list.html';
      $scope.selection = null;
      $scope.listener = function () {
        var oldSelection = $scope.selection;
        $scope.selection = window.getSelection().toString();
        if ($scope.selection.length > 0 && $scope.selection !== oldSelection) {
          $http.get('/api/v1/phrases?traditional=' + encodeURIComponent($scope.selection))
          .then(function (response) {
            $scope.phrases = response.data.results;
          });
        }
      };
      $scope.editMode = false;
      $scope.toggleEditMode = function () {
        $scope.data.processedText = $scope.text.processed_text;
        $scope.editMode = !$scope.editMode;
      };
      $scope.save = function () {
        $scope.editMode = false;
        $scope.text.text = $scope.data.processedText;
        $http.put(API_BASE_URL + 'texts/' + $routeParams.id, $scope.text)
        .then(function (response) {
          $scope.text = response.data;
          $scope.data.processedText = $scope.text.processed_text;
        });
      };
    }]);


    app.controller('TextEditCtrl', [
      '$scope', '$http', '$routeParams',
      function ($scope, $http, $routeParams) {
        $http.get(API_BASE_URL + 'texts/' + $routeParams.id)
        .then(function (response) {
          $scope.text = response.data;
          if ($scope.text.owner.id != USER_ID) {
            // TODO: raise error
          }
        });
        $scope.finish = function () {
          window.location.href = '#/texts/' + $routeParams.id;
        };
        $scope.submit = function (isValid) {
          if (isValid) {
            $http.put(API_BASE_URL + 'texts/' + $routeParams.id, $scope.text)
            .then(function (response) {
              $scope.finish();
            }, function (response) {
              $scope.error = response.data;
            });
          }
        };
      }]);


    app.controller('TextCreateCtrl', [
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
      }]);

    app.controller('SearchCtrl', [
      '$scope', '$http', '$routeParams', 'phraseService',
      function ($scope, $http, $routeParams, phraseService) {
        $scope.phraseService = phraseService;
        $scope.search_query = $routeParams.query;
        $scope.phrases = {};
        $scope.more = function () {
          $http.get($scope.data.next).then(function (response) {
            $scope.data = response.data;
            for (var i in response.data.results)
              $scope.phrases.push(response.data.results[i]);
          });
        }
        $http.get(API_BASE_URL + 'phrases?q='
                  + encodeURIComponent($routeParams.query) + '&lang='
                  + encodeURIComponent($routeParams.lang))
        .then(function (response) {
          $scope.data = response.data;
          $scope.phrases = response.data.results;
        });
      }]);

    app.controller('StarredPhrasesCtrl', [
      '$scope', '$http', 'phraseService',
      function ($scope, $http, phraseService) {
        $scope.phraseService = phraseService;
        $scope.phrases = {};
        $scope.more = function () {
          $http.get($scope.data.next).then(function (response) {
            $scope.data = response.data;
            for (var i in response.data.results)
              $scope.phrases.push(response.data.results[i]);
          });
        }
        $http.get(API_BASE_URL + 'phrases?starred=true')
        .then(function (response) {
          $scope.data = response.data;
          $scope.phrases = response.data.results;
        });
      }
    ]);

    app.controller('SearchFormCtrl', ['$scope', function ($scope) {
      $scope.lang = 'zh-tw';
      $scope.search = function () {
        window.location.href = ('#/search/' + encodeURIComponent($scope.lang)
                                + '/' + encodeURIComponent($scope.query));
      };
    }]);


})();
