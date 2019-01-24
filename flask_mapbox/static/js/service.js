$(document).ready(function () {

  let year_select = document.getElementById("year-selector");
  let output = document.getElementById("demo");

  output.innerHTML = year_select.value; // Display the default slider value

  //get values from year selectbox
  $('#data-selector-form').on('change', function(e) {
    $.ajax({
        data: {year : $('#year-selector').val(),
              nationality: $('input[name=nationality]:checked').val(),
              gender: $("input[name=gender]:checked").val()
        },
        type: 'POST',
        url: '/mapupdate/'
    })
    .done(function(data){

        let $map = $('#folium-map').contents().clone();
        let $new_map = $(data);
        $('#folium-map').empty();
        $('#folium-map').append($new_map);
    });
    e.preventDefault();
  });

  //get values from gender radiobox
  // $('input[name=gender]').on('change', function (e) {
  //   $.ajax({
  //       data: {gender: $("input[name=gender]:checked").val()},
  //       type: 'POST',
  //       url: '/mapupdate/'
  //   })
  //   .done(function (data) {
  //       let $map = $('#folium-map').contents().clone();
  //       let $new_map = $(data);
  //       $('#folium-map').empty();
  //       $('#folium-map').append($new_map);
  //   });
  //
  // });



});



