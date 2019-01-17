var slider = document.getElementById("year-selector");
var output = document.getElementById("demo");
output.innerHTML = slider.value; // Display the default slider value
console.log(slider.value);

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
}