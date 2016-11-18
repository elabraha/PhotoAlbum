function makeFavoritePostRequest(picid, latest_favorite, fb) {
  var data = {
    'id': picid,
    'latest_favorite': latest_favorite
  };
  //console.log(data);

  qwest.post('/ofvujvy4x6r/pa3/pic/favorites', data, {
    dataType: 'json',
    responseType: 'json'
  }).then(function(xhr, resp) {
    fb(resp);
  });
}

function makeFavoriteRequest(picid, fb) {
  // console.log("from make request");
  // console.log(picid);
  qwest.get('/ofvujvy4x6r/pa3/pic/favorites?id=' + picid)
    .then(function(xhr, resp) {
      fb(resp);
    });
}

function initFavorite(picid, latest_favorite) {
  // console.log(picid);
  // console.log(captionBinding)
  //var favorite_display = getElementById("favorite_display");

  makeFavoriteRequest(picid, function(resp) {
    console.log(resp['num_favorites']);
    console.log(resp['latest_favorite']);
    console.log("here");
    document.getElementById("favorite_display").innerHTML = resp['num_favorites'] + " favorites, most recently favorited by " + resp['latest_favorite'];
    console.log(resp);
  });

  setInterval(function() {
   makeFavoriteRequest(picid, function(resp) {
      console.log(resp['num_favorites']);
      console.log(resp['latest_favorite']);
      document.getElementById("favorite_display").innerHTML = resp['num_favorites'] + " favorites, most recently favorited by " + resp['latest_favorite'];
      console.log(resp);
    }); 
  }, 10000);

  //document.getElementById("caption_display").innerHTML = captionBinding.element.data;
}