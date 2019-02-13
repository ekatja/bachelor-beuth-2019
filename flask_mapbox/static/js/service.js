$(document).ready(function () {

    // let year_select = document.getElementById("year-slider");
    // let output = document.getElementById("year-slider-val");
    //
    // output.innerHTML = year_select.value; // Display the default slider value
    //
    //   $('#year-slider').on('input', function (e) {
    //       output.innerText = year_select.value;
    //   });

    // console.log(window.location);
    //
    //get values from year, nationality and gender selectbox

    console.log("Ready to work!");

    $('#data-selector-form').on('change', function (e) {

        console.log("Changed data selector");
        console.log(window.location.pathname);
        console.log($('#data-selector').val());
        switch ($('#data-selector').val()) {

            case 'st_bd': {
                console.log('case: st_bd');
                window.location = "/map/";
                break;
            }
            case 'university-foundation-year': {
                console.log('case: university-foundation-year');
                window.location = "/university-foundation-year/";
                break;
            }
            case 'place-of-study': {
                console.log('case: place-of-study');
                window.location = "/place-of-study/";
                break;
            }
        }
        e.preventDefault();
    });

    $('#options-selector-form').on('change', function (e) {
        console.log("options change", e);
        console.log('Changed option selector');
        console.log(window.location.pathname);

        switch(window.location.pathname){
            case '/map/': {
                console.log('case: options by map')
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
                        console.log|(data);
                        let $map = $('#folium-map').contents().clone();
                        let $new_map = $(data);
                        //TODO: Optimize map include
                        $('#folium-map').empty();
                        $('#folium-map').append($new_map);

                    });
                console.log($('input[name=nationality]:checked').val());
                break;
            }
            case '/university-foundation-year/': {
                console.log('case: options by university-foundation-year');
                $.ajax({
                    data: {
                        dataframe: $('#data-selector').val(),
                        // year: $('output#slider-value').val(),
                        // nationality: $('input[name=nationality]:checked').val(),
                        // gender: $("input[name=gender]:checked").val()
                    },
                    type: 'POST',
                    url: '/mapupdate/'
                    // url: '/update-university-foundation-year/'
                })
                    .done(function (data) {
                        // //TODO: Optimize map include
                    });
                break;
            }
            case '/place-of-study/':{
                console.log('case: options by place-of-study');
                $.ajax({
                    data: {
                        dataframe: $('#data-selector').val(),
                        year: $('#year-selector').val(),
                        // nationality: $('input[name=nationality]:checked').val(),
                        gender: $("input[name=gender]:checked").val(),
                        state: $('#state-selector').val()
                    },
                    type: 'POST',
                    url: '/study-place-mapupdate/'
                })
                    .done(function (data) {
                        let $map = $('#folium-map').contents().clone();
                        let $new_map = $(data);
                        //TODO: Optimize map include
                        $('#folium-map').empty();
                        $('#folium-map').append($new_map);
                    });
                break;
            }
            e.preventDefault();
        }
    });

    $('#year-slider').on('change', function (e) {

        $.ajax({
            data: {
                dataframe: $('#data-selector').val(),
                year: $('output#slider-value').val(),
            },
            type: 'POST',
            url: '/update-university-foundation-year/'
        })
            .done(function (data) {

            });

        e.preventDefault();
    });

});



