var $ = function(selector) {
  return document.querySelector(selector);
};

function sendPostRequest(url, parameters, callback) {
  var request = new XMLHttpRequest();
  request.onreadystatechange = function () {
    if (request.readyState == 4 && request.status == 200) {
      callback(request.responseText);
    }
  }
  request.open('POST', url, true);
  request.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  request.send(parameters); 
}

function formSubmitHandler() {
  var param = "email=" + $("#signup-email").value;
  sendPostRequest("/signup-form", param, function (responseText) {
                    alert(responseText);
                  });
  return false;
}

window.addEventListener('load', function () {
    $('form').onsubmit = formSubmitHandler;
  });


