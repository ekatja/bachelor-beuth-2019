$(document).ready(function () {

    // let year_select = document.getElementById("year-slider");
    // let output = document.getElementById("year-slider-val");
    //
    // output.innerHTML = year_select.value; // Display the default slider value
    //
    //   $('#year-slider').on('input', function (e) {
    //       output.innerText = year_select.value;
    //   });

    console.log(window.location);

    //get values from year, nationality and gender selectbox
    $('#data-selector-form').on('change', function (e) {

        console.log("Changed data selector");

        if ($('#data-selector').val() == "university-foundation-year") {
            window.location = "/university-foundation-year";
            //       // $('#data-selector option[value="university-foundation-year"]').attr('selected', true);
        }
        else {

            if (window.location.pathname.includes("university-foundation-year")) {
                if ($('#data-selector').val() == "st_bd") {
                    window.location = "/map";
                }
            }

            else {

                $.ajax({
                    data: {
                        dataframe: $('#data-selector').val(),
                        year: $('#year-selector').val(),
                        nationality: $('input[name=nationality]:checked').val(),
                        gender: $("input[name=gender]:checked").val()
                    },
                    type: 'POST',
                    url: '/mapupdate/'
                })
                    .done(function (data, statusText, xhr) {
                        //console.log(data.dataframe);
                        // if (xhr.status == 200) {
                        let $map = $('#folium-map').contents().clone();
                        let $new_map = $(data);
                        //TODO: Optimize map include
                        $('#folium-map').empty();
                        $('#folium-map').append($new_map);
                        // } else {
                        //     console.error("xhr:", xhr);
                        //     console.error("data:", data);
                        // }
                    });

                e.preventDefault();
            }
        }
    });

});



