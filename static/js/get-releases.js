/**
 * Created by Peter.Makafan on 4/13/2016.
 */

var projectId = $("#projectId").val();


var Release = function (release) {
  var self = this;
    self.assembled = ko.observable(release.assembled);
    self.id = ko.observable(release.id);
    self.version = ko.observable(release.version);
    return self;
};

var AppViewModel = function(){
    var self = this;

    self.releases = ko.observableArray([]);
    self.pageSize = ko.observable(10);
    self.currentPageIndex = ko.observable(0);
    self.search = ko.observable("");
    self.dirty = ko.observable(false);
    self.currentLength = ko.observable(0);
    self.latest = ko.observable(new Release({}));

    self.currentPage = ko.computed(function () {
        var filter = self.search().toLowerCase();
        if (!filter) {
            self.currentLength(self.releases().length);
            var pagesize = parseInt(self.pageSize(), 10);
            var startIndex = pagesize * self.currentPageIndex();
            var endIndex = startIndex + pagesize;
            return self.releases.slice(startIndex, endIndex);
        } else {
            var releases = ko.utils.arrayFilter(self.releases(), function (issue) {
                return ko.utils.stringStartsWith(issue.key().toLowerCase(), filter);
            });
            var length = issues.length;
            self.currentLength(length);
            self.dirty() ? self.currentPageIndex(0) : 0;
            var currentIndex = parseInt(self.currentPageIndex(), 10);
            var pagesize = parseInt(self.pageSize(), 10);
            var startIndex = pagesize * currentIndex;
            var endIndex = startIndex + pagesize;
            self.dirty(false);
            return releases.slice(startIndex, endIndex);;
        }

    }, self);

     self.dirtyCalculations = ko.computed(function () {
        self.search();
        self.dirty(true);
    });

    self.nextPage = function () {
        if (((self.currentPageIndex() + 1) * self.pageSize()) < self.currentLength()) {
            self.currentPageIndex(self.currentPageIndex() + 1);
        }
        else {
            self.currentPageIndex(0);
        }
    };
    self.previousPage = function () {
        if (self.currentPageIndex() > 0) {
            self.currentPageIndex(self.currentPageIndex() - 1);
        }
        else {
            self.currentPageIndex((Math.ceil(self.currentLength() / self.pageSize())) - 1);
        }
    };


    $.getJSON('/project/releases/'+projectId ,function (data) {
        self.releases(ko.utils.arrayMap(data.releases, function (i) {
       return new Release(i);
    }));
        self.latest(new Release(data.releases[0]));
    } );

 };



$(document).ready(function () {
    ko.applyBindings(new AppViewModel());
});
