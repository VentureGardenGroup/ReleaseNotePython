/**
 * Created by Peter.Makafan on 4/10/2016.
 */
/* global ko */

var projectId = $('#projectId').val();
var jiraUrl = 'http://projects.splasherstech.com:8080/browse/';

ko.utils.stringStartsWith = function (string, startsWith) {
    string = string || "";
    if (startsWith.length > string.length)
        return false;
    return string.substring(0, startsWith.length) === startsWith;
};

var Issue = function(issue){
    var self = this;
    self.key = ko.observable(issue.key);
    self.summary = ko.observable(issue.summary);
    self.description = ko.observable(issue.description);
    self.status = ko.observable(issue.status_name);
    self.issueType = ko.observable(issue.issue_type);
    return self;
};


var AppViewModel = function(){
    var self = this;

    self.issues = ko.observableArray([]);
    self.pageSize = ko.observable(5);
    self.currentPageIndex = ko.observable(0);
    self.search = ko.observable("");
    self.dirty = ko.observable(false);
    self.currentLength = ko.observable(0);
    self.checkedIssuesKeys = ko.observableArray();
    self.checkedIssues =  ko.observableArray();

    self.currentPage = ko.computed(function () {
        var filter = self.search().toLowerCase();
        if (!filter) {
            self.currentLength(self.issues().length);
            var pagesize = parseInt(self.pageSize(), 10);
            var startIndex = pagesize * self.currentPageIndex();
            var endIndex = startIndex + pagesize;
            return self.issues.slice(startIndex, endIndex);
        } else {
            var issues = ko.utils.arrayFilter(self.issues(), function (issue) {
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
            return issues.slice(startIndex, endIndex);;
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

    self.selectTicket = function (data, elem) {
        var hiddenElement = $('#releasenote');
        var hiddenText = hiddenElement.val();
        var $checkBox = $(elem.currentTarget);
        var checked = $checkBox.is(':checked');
        var issueType = data.issueType();
        if("bug" ==issueType.toLowerCase()){
            issueType+= " Fix";
        }
        var issueUrl = "<a href="+jiraUrl+data.key()+" target='_blank'>"+data.key()+"</a>";
        var value  = '<p>'+ issueUrl+ " - "+"<b>"+ issueType +"</b>" + ' - ' + data.summary() +'</p>' ;
            if (checked) {
                var list = hiddenText.split('||');
                var index = list.indexOf(value);
                if (index < 0) {
                    hiddenText += value + '||';
                    hiddenElement.val(hiddenText)
                    self.checkedIssues.push(data);
                }
            }
            else {
                var list = hiddenText.split('||');
                var index = list.indexOf(value);
                if (index >= 0) {
                    list.splice(index, 1);
                    hiddenText = list.join('||');
                    hiddenElement.val(hiddenText);
                    self.checkedIssues.remove(data);

                }

            }
        return true;
    };

    $.getJSON('/issues/'+projectId ,function (data) {
        self.issues(ko.utils.arrayMap(data.tickets, function (i) {
       return new Issue(i);
    }));
    } );

 };



$(document).ready(function () {
    ko.applyBindings(new AppViewModel());
});
