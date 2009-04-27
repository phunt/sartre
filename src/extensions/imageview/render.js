$(document).ready(function() {
  $(".tx").each(function(i) {
    $(this).html($(this).html().replace(
                     /http:\/\/(www.)?twitpic.com\/([a-zA-Z0-9]+)/g,
                     "<img src='http://twitpic.com/show/mini/$2'/>"));
  });
});
