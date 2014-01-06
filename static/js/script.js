var RED = 'rgb(176,0,0)';
var GREEN = 'rgb(77, 189, 51)';

var $ = function (selector) {
  return document.querySelector(selector);
};

/* Utility function to send a post request. */
function sendPostRequest(url, parameters, callback) {
  var request = new XMLHttpRequest();
  request.onreadystatechange = function () {
    if (request.readyState == 4 && request.status == 200) {
      callback(request.responseText);
    }
  }
  request.open('POST', url, true);
  request.setRequestHeader('Content-type','application/x-www-form-urlencoded');
  request.send(parameters); 
}

/* Shows and then fades a feedback message with the specified color. */
function showFeedback(message, color) {
  var feedbackElem = $('#feedback');
  feedbackElem.className = '';

  feedbackElem.style.opacity = 1;
  feedbackElem.style.visibility = 'visible';
  feedbackElem.style.color = color;
  feedbackElem.innerText = message;

  // We want the element to fade out but not fade in.
  // If we apply the class synchronously, it fades in.
  // Hence, we wrap the fade-out logic in a rAF.
  window.requestAnimationFrame(function () {
    feedbackElem.className = 'fade';
    feedbackElem.style.opacity = .0;
    feedbackElem.style.visibility = 'hidden';
  });
}

/* Callback for signup form submission response from server. */
function formCallback(responseText) {
  var message = '';
  var color = RED;

  switch (parseInt(responseText)) {
    case 0:
      message = 'Welcome! You\'ll get a confirmation email soon.';
      color = GREEN;
      break;
    case 1:
      message = 'Looks like you\'re already signed up :)';
      color = GREEN;
      break;
    case 2:
      message = 'Oops! Please enter an email address.';
      break;
    case 3:
      message = 'Oops! Please enter a valid email address.';
      break;
    default:
      message = 'Oops. Something went wrong. Try again later.';
  }

  showFeedback(message, color);
}

function formSubmitHandler() {
  var param = $('#signup-email').value;
  if (false && !param) {
    showFeedback('Oops! Please enter an email address.', RED);
    return false;
  }
  param = 'email=' + param; 
  sendPostRequest('/signup-form', param, formCallback);
  return false;
}

window.addEventListener('load', function () {
    $('form').onsubmit = formSubmitHandler;
  });


