var year_select = document.getElementById("year-selector");
var output = document.getElementById("demo");
output.innerHTML = year_select.value; // Display the default slider value
console.log(year_select.value);
console.log(window.location);
var loc;
var path = window.location.pathname;

// Update the current slider value (each time you drag the slider handle)
year_select.oninput = function() {
  output.innerHTML = this.value;

  loc = window.location;
  loc.href = this.value;
}

