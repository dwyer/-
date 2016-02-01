'use strict';

var app = angular.module('yanjiu', ['ngRoute']);

app.config(function($httpProvider) {
  $httpProvider.defaults.headers.common['X-CSRFToken'] = CSRF_TOKEN;
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});

app.config(['$routeProvider', function ($routeProvider) {
  $routeProvider
  .when('/texts', {
    templateUrl: PARTIALS_DIR + 'text_list.html',
    controller: 'TextListCtrl'
  })
  .when('/texts/:id', {
    templateUrl: PARTIALS_DIR + 'text_detail.html',
    controller: 'TextDetailCtrl'
  })
  .when('/texts/:id/edit', {
    templateUrl: PARTIALS_DIR + 'text_edit.html',
    controller: 'TextEditCtrl'
  })
  .otherwise({redirectTo: '/'});
}]);

app.controller('TextListCtrl', ['$scope', '$http', function($scope, $http) {
  $http({
    method: 'GET',
    url: '/api/v1/texts'
  }).then(function (response) {
    $scope.texts = response.data.results;
  });
}]);

app.controller('TextDetailCtrl', [
    '$scope',
    '$http',
    '$routeParams',
    function($scope, $http, $routeParams) {
      $http({
        method: 'GET',
        url: '/api/v1/texts/' + $routeParams.id
      }).then(function (response) {
        $scope.text = response.data;
        $scope.isWritable = $scope.text.owner === USER_USERNAME;
      });
      $scope.phraseListPartialUrl = PARTIALS_DIR + 'phrase_list.html';
      $scope.selection = null;
      $scope.playAudio = function(phrase) {
        var url = '/audio/' + phrase + '.mp4';
        var audio = new Audio(url);
        audio.play();
      };
      $scope.listener = function () {
        if (window.getSelection) {
          $scope.selection = window.getSelection().toString();
        } else {
          $scope.selection = document.selection.createRange().text;
        }
        if ($scope.selection.length > 0) {
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
    '$scope',
    '$http',
    '$routeParams',
    '$window',
    function($scope, $http, $routeParams, $window) {

      var id = $routeParams.id;

      $http({
        method: 'GET',
        url: API_BASE_URL + 'texts/' + id
      }).then(function (response) {
        $scope.text = response.data;
        if ($scope.text.owner !== USER_USERNAME) {
          // TODO: raise error
        }
      });

      $scope.cancel = function() {
        $window.location.href = '#/texts/' + id;
      };

      $scope.submit = function () {
        if ($scope.text) {
          $http({
            method: 'PUT',
            url: API_BASE_URL + 'texts/' + id,
            data: $scope.text
          }).then(function (response) {
            $scope.cancel();
          });
        }
      };

}]);
