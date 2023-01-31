var label = document.querySelector('nav label');
var hamburger = document.getElementById('hamburger');
label.addEventListener('click', hamburgerClick);
function hamburgerClick() {
  if (hamburger.checked) {
    label.innerHTML = '&#9776;';
  } else {
    label.innerHTML = '✖';
  }
}
