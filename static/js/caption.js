function Caption(element, picid, caption) {
  this.element = element;
  this.picid = picid;
  element.value = caption; // objects in Javascript are assigned by reference, so this works
  element.addEventListener("change", this, false); 
}

Caption.prototype.handleEvent = function(e) {
  if (e.type === "change") {
    this.update(this.element.value);
    // document.getElementById("caption_display").innerHTML = this.element.value;
  }
}

Caption.prototype.change = function(value) {
  this.data = value;
  this.element.value = value;
}

Caption.prototype.update = function(caption) {
  makeCaptionPostRequest(this.picid, caption, function() {
    console.log('POST successful.');
  });
}

function makeCaptionPostRequest(picid, caption, cb) {
  var data = {
    'id': picid,
    'caption': caption
  };

  qwest.post('/ofvujvy4x6r/pa3/pic/caption', data, {
    dataType: 'json',
    responseType: 'json'
  }).then(function(xhr, resp) {
    cb(resp);
  });
}

function makeCaptionRequest(picid, cb) {
  // console.log("from make request");
  // console.log(picid);
  qwest.get('/ofvujvy4x6r/pa3/pic/caption?id=' + picid)
    .then(function(xhr, resp) {
      cb(resp);
    });
}

function initCaption(picid) {
  var caption = document.getElementById("caption");
  // console.log("from initCaption");
  // console.log(caption.value);
  var captionBinding = new Caption(caption, picid);
  // console.log(picid);
  console.log(captionBinding)
  makeCaptionRequest(picid, function(resp) {
    captionBinding.change(resp['caption']);
  });

  setInterval(function() {
   makeCaptionRequest(picid, function(resp) {
      captionBinding.change(resp['caption']);
    }); 
  }, 7000);

}