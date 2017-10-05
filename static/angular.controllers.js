var msw = angular.module('myApp', ['ngSanitize']);

msw.controller('FiltersCtrl', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) {
    $scope.filters = []
    $http.get('/msw/api/v1/filters/?format=json')
        .then(function(response) {
            $scope.filters = response.data.objects;
        })

    $scope.letters = []
    $scope.loadLettersByFilterId = function(filter_id) {
        $http.get('/msw/api/v1/filters-finds-letters/?format=json&filter_id=' + filter_id.toString())
            .then(function(response) {
                $scope.letters = response.data.objects;
            })

    }

    $scope.loadLetter = function(id, commonData) {
        $rootScope.$broadcast('loadLetter', {'id': id, 'common': commonData})
    }
}]);


msw.controller('AccountsErrorsCtrl', ['$scope', '$http', function($scope, $http) {
    $scope.errors = []
    $scope.loadErrorsList = function(account_id) {
        $http.get('/msw/api/v1/accounts-errors/?format=json&account_id=' + account_id)
            .then(function(response) {
                $scope.errors = response.data.objects;
            })
    }


}]);

msw.controller('AccountsCtrl', ['$scope', '$http', function($scope, $http) {
    $scope.accounts = []
    $http.get('/msw/api/v1/accounts/?format=json')
        .then(function(response) {
            $scope.accounts = response.data.objects;
        })
}]);

msw.controller('StatsCtrl', ['$scope', '$http', function($scope, $http) {
    $scope.accounts = []
    $http.get('/msw/api/v1/stats/?format=json')
        .then(function(response) {
            $scope.accounts = response.data.objects;
            console.log($scope.accounts)
        })
}]);

msw.controller('FoldersCtrl', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) {
    $scope.folders = []
    $http.get('/msw/api/v1/folders/?format=json&account_id=' + $scope.account.id)
        .then(function(response) {
            $scope.folders = response.data.objects;
        })
    $scope.loadFolder = function(id) {
        $rootScope.$broadcast('loadLettersForFolder', id)
    }

    $scope.substrcount = function (string, subString, allowOverlapping) {
        string += "";
        subString += "";
        if (subString.length <= 0) return (string.length + 1);

        var n = 0,
            pos = 0,
            step = allowOverlapping ? 1 : subString.length;

        while (true) {
            pos = string.indexOf(subString, pos);
            if (pos >= 0) {
                ++n;
                pos += step;
            } else break;
        }
        return n;
    }
}]);

msw.controller('LettersListCtrl', ['$rootScope', '$scope', '$http', function($rootScope, $scope, $http) {
    $scope.letters = []
    $scope.$on('loadLettersForFolder', function(event, folderId) {
        $http.get('/msw/api/v1/subjects/?format=json&folder_id=' + folderId)
            .then(function(response) {
                $scope.letters = response.data.objects;
            })
    });
    $scope.loadLetter = function(id) {
        $rootScope.$broadcast('loadLetter', {'id': id})
    }
}]);

msw.controller('LetterCtrl', ['$scope', '$http', function($scope, $http) {
    $scope.letter = {}
    $scope.$on('loadLetter', function(event, letterData) {
        $http.get('/msw/api/v1/letters/' + letterData.id + '/?format=json')
            .then(function(response) {
                var commonData = letterData.common
                $scope.letter = commonData ? $scope.filterHighlight(response.data, commonData) : response.data;
            })
    });
    $scope.filterHighlight = function (letterObject, filterData) {
        if (filterData['filter_content'] != undefined) {
            if (filterData['filter_type'] == 'str') {
                if (filterData['filter_target'] == 'content') {
                    letterObject.body = $scope.highlightByStr(filterData['filter_content'], letterObject.body)
                }
                if (filterData['filter_target'] == 'subject') {
                    letterObject.subject = $scope.highlightByStr(filterData['filter_content'], letterObject.subject)
                }
                if (filterData['filter_target'] == 'from') {
                    letterObject.from_name = $scope.highlightByStr(filterData['filter_content'], letterObject.from_name)
                    letterObject.from_mail = $scope.highlightByStr(filterData['filter_content'], letterObject.from_mail)
                }
                if (filterData['filter_target'] == 'to') {
                    letterObject.to_name = $scope.highlightByStr(filterData['filter_content'], letterObject.to_name)
                    letterObject.to_mail = $scope.highlightByStr(filterData['filter_content'], letterObject.to_mail)
                }
            }
            if (filterData['filter_type'] == 'regex') {
                if (filterData['filter_target'] == 'content') {
                    letterObject.body = $scope.highlightByRegex(filterData['filter_content'], letterObject.body)
                }
                if (filterData['filter_target'] == 'subject') {
                    letterObject.subject = $scope.highlightByRegex(filterData['filter_content'], letterObject.subject)
                }
                if (filterData['filter_target'] == 'from') {
                    letterObject.from_name = $scope.highlightByRegex(filterData['filter_content'], letterObject.from_name)
                    letterObject.from_mail = $scope.highlightByRegex(filterData['filter_content'], letterObject.from_mail)
                }
                if (filterData['filter_target'] == 'to') {
                    letterObject.to_name = $scope.highlightByRegex(filterData['filter_content'], letterObject.to_name)
                    letterObject.to_mail = $scope.highlightByRegex(filterData['filter_content'], letterObject.to_mail)
                }
            }
        }
        return letterObject
    }
    $scope.highlightByStr = function (highlightPhrase, targetStr) {
        return targetStr.split(highlightPhrase).join("<font color='red'><b>" + highlightPhrase + "</b></font>")
    }
    $scope.highlightByRegex = function (highlightPhrase, targetStr) {
        return targetStr.replace(new RegExp('(' + highlightPhrase + ')', 'gi'), "<font color='red'><b>$1</b></font>")
    }
}]);

msw.controller('AttachmentsCtrl', ['$scope', '$http', function($scope, $http) {
    $scope.attachments = {}
    $scope.$on('loadLetter', function(event, letterData) {
        $http.get('/msw/api/v1/attachments/?format=json&letter_id='+ letterData.id)
            .then(function(response) {
                $scope.attachments = response.data.objects;
            })
    });
}]);

msw.controller('AttachmentsListCtrl', ['$scope', '$http', function($scope, $http) {
    $scope.attachments = {}

    $scope.loadFilesList = function (ext) {
        $http.get('/msw/api/v1/attachments-list/?format=json&ext__exact=' + ext)
            .then(function(response) {
                $scope.attachments = response.data.objects;
            })
    }
}]);