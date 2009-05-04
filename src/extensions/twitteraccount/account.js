public_timeline = function(callback) {
    requestURL = "http://twitter.com/statuses/public_timeline.json?callback=?";
    $.getJSON(requestURL, callback);
}

function twitter_poll(store) {
  public_timeline(function(json, status) {
      $.each(json, function(i) {
        store.add({'screen_name':this['user']['screen_name'],
                  'text':this['text']});
      });
      store.done();
    });
}
