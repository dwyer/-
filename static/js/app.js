'use strict';

(function () {
  var app = angular.module('yanjiu', [
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
    .otherwise({redirectTo: '/'});
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
    $http({
      method: 'GET',
      url: '/api/v1/texts?fields=id,title,video_url'//,
    }).then(function (response) {
      $scope.texts = response.data.results;
    });
  }]);


  app.controller('TextDetailCtrl', [
    '$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
      $http({
        method: 'GET',
        url: '/api/v1/texts/' + $routeParams.id//,
      }).then(function (response) {
        $scope.text = response.data;
        $scope.isWritable = $scope.text.owner.id == USER_ID;
      });
      $scope.phraseListPartialUrl = PARTIALS_DIR + 'phrase_list.html';
      $scope.selection = null;
      $scope.playAudio = function (phrase) {
        var url = '/audio/' + phrase + '.mp4';
        var audio = new Audio(url);
        audio.play();
      };
      $scope.listener = function () {
        var oldSelection = $scope.selection;
        if (window.getSelection) {
          $scope.selection = window.getSelection().toString();
        } else {
          $scope.selection = document.selection.createRange().text;
        }
        if ($scope.selection.length > 0 && $scope.selection !== oldSelection) {
          $http({
            method: 'GET',
            url: '/api/v1/phrases?traditional=' + encodeURIComponent($scope.selection)
          }).then(function (response) {
            $scope.phrases = response.data.results;
          });
        }
      };
    }]);


    app.controller('TextEditCtrl', [
      '$scope', '$http', '$routeParams',
      function ($scope, $http, $routeParams) {
        var id = $routeParams.id;
        $http({
          method: 'GET',
          url: API_BASE_URL + 'texts/' + id//,
        }).then(function (response) {
          $scope.text = response.data;
          if ($scope.text.owner.id != USER_ID) {
            // TODO: raise error
          }
        });
        $scope.finish = function () {
          window.history.back();
        };
        $scope.submit = function (isValid) {
          if (isValid) {
            $http.put(API_BASE_URL + 'texts/' + id, $scope.text)
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
          window.history.back();
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


})();
