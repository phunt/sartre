$(document).ready(function() {
  $(".sn").each(function(i) {
     $(this).html("<a href='http://twitter.com/" + $(this).html() + "'>"
                  + $(this).html() + "</a>");
  });
  $(".tx").each(function(i) {
     $(this).html($(this).html().replace(/@([a-zA-Z0-9]+)/g,
                          "<a href='http://twitter.com/$1'>@$1</a>"));
  });
});
