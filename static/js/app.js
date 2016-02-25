'use strict';

(function () {

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

    $rootScope.playAudio = function (text) {
      var url = API_BASE_URL + 'audio/' + text + '.mp4';
      var audio = new Audio(url);
      audio.play();
    };

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


  /**
   * Wrap Chinese sentences in a span.zh-sent tag.
   * TODO: lookup words.
   */
  .filter('processText', ['$sce', function ($sce) {

    var cache = {};

    function lookup(term) {
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
  }])


  .controller('TextListCtrl', ['$scope', '$http', function ($scope, $http) {
    $http.get('/api/v1/texts?fields=id,title,video_url')
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

      $scope.selectTerm = function (selection) {
        var oldSelection = $scope.selection;
        $scope.selection = selection;
        if ($scope.selection.length > 0 && $scope.selection !== oldSelection) {
          $http.get('/api/v1/terms?traditional='
                    + encodeURIComponent($scope.selection))
          .then(function (response) {
            $scope.terms = response.data.results;
          });
        }
      };

      $scope.listener = function () {
        $scope.selectTerm(window.getSelection().toString());
      };

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

      $http.get('/api/v1/texts/' + $routeParams.id)
      .then(function (response) {
        $scope.text = response.data;
        $scope.data.processedText = $scope.text.processed_text;
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
