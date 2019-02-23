$(document).ready(function () {

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
                console.log('case: options by map');
                $.ajax({
                    data: {
                        dataframe: $('#data-selector').val(),
                        year: $('#slider-value').val(),
                        nationality: $('input[name=nationality]:checked').val(),
                        gender: $("input[name=gender]:checked").val()
                    },
                    type: 'POST',
                    url: '/mapupdate/'
                })
                    .done(function (data, statusText, xhr) {
                        // console.log(data);
                        $('#ws').text("Wintersemester "+data.year+', '+data.nationality+', '+data.gender);
                        // let $map = $('#folium-map').contents().clone();
                        // let $new_map = $(data.map);
                        // //TODO: Optimize map include
                        // $('#folium-map').empty();
                        // $('#folium-map').append('<div id = \'legend-bg\'></div>');
                        // $('#folium-map').append($new_map);

                    });
                console.log($('input[name=nationality]:checked').val());
                break;
            }
            case '/university-foundation-year/': {
                console.log('case: options by university-foundation-year');
                $.ajax({
                    data: {
                        dataframe: $('#data-selector').val(),

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
                        $('#ws').text("Wintersemester "+data.year+', '+data.state+', '+data.gender);
                        let $map = $('#folium-map').contents().clone();
                        let $new_map = $(data.map);
                        //TODO: Optimize map include
                        $('#folium-map').empty();
                        $('#folium-map').append('<div id = \'legend-bg\'></div>');
                        $('#folium-map').append($new_map);
                    });
                break;
            }
            e.preventDefault();
        }
    });


    $('#year-slider-uni').on('input', function (e) {

        $.ajax({
            type: 'GET',
            url: '/bokeh_data/'+$('#year-slider-uni').find('output#slider-value').val()
        })
            .done(function (data) {

                let ds = Bokeh.documents[0].get_model_by_name('students');
                ds.data = data.source.data;
                console.log(ds.data);
                ds.change.emit();

                let currentYear = $('#year-slider-uni').find('output#slider-value').val();
                let tableData = data.table;
                let uniAll = 0, hsAll = 0, kmhAll = 0, otherAll = 0, resultAll = 0;

                let uni = tableData[currentYear].uni;
                let hs = tableData[currentYear].hs;
                let kmh = tableData[currentYear].kmh;
                let other = tableData[currentYear].other;
                let result = uni+hs+kmh+other;
                console.log(currentYear);

                $('#uni-year').text(currentYear);
                $('#uni').text(uni);
                $('#hs').text(hs);
                $('#kmh').text(kmh);
                $('#other').text(other);
                $('#result-year').text(result);

                for (let year in tableData){

                    if ( year <= currentYear){
                        console.log("year:" + year, "currentYear: "+currentYear);
                        uniAll += tableData[year].uni;
                        hsAll += tableData[year].hs;
                        kmhAll += tableData[year].kmh;
                        otherAll += tableData[year].other;

                    }
                }
                $('#uni-all').text(uniAll);
                $('#hs-all').text(hsAll);
                $('#kmh-all').text(kmhAll);
                $('#other-all').text(otherAll);


            });

        $.ajax({
            data: {
                dataframe: $('#data-selector').val(),
                year: $('#year-slider-uni').find('output#slider-value').val(),
            },
            type: 'POST',
            url: '/update-university-foundation-year/'
        })
            .done(function (data) {
                // console.log(data.year);
                // $('#uni-year').text(data.year);
            });
        e.preventDefault();
    });

    $('.btn-showinfo').click(function () {
        $('.statistic-content').toggleClass('open-info');
        $(this).find('i').toggleClass('fa-angle-up fa-angle-down');

    });


});



