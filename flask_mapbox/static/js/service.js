var loc, index;

var year_select = document.getElementById("year-selector");
var output = document.getElementById("demo");

if(localStorage.getItem('selected_year')) {
  // Retrieve selected year from local storage
  document.getElementById("year-selector").selectedIndex = localStorage.getItem("selected_year");
  output.innerHTML = year_select.value;
} else {
  output.innerHTML = year_select.value; // Display the default slider value
}

// Update the current slider value (each time you drag the slider handle)
year_select.oninput = function() {

  output.innerHTML = this.value;
  index = year_select.selectedIndex;
  // Store selected year in local storage
  localStorage.setItem("selected_year", index);

  loc = window.location;
  loc.href = this.value;
}

