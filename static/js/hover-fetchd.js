/* https://stackoverflow.com/a/18032363 */

var static = new Image();
static.src = "/static/icons/farfetchd-static.png";
var animated = new Image();
animated.src = "/static/icons/farfetchd-animated.png";

function hover() {
  document.querySelector("header img").setAttribute('src', animated.src);
}

function unhover() {
  document.querySelector("header img").setAttribute('src', static.src);
}