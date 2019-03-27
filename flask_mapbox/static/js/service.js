$(document).ready(function () {

    console.log("Ready to work!");

    if (document.getElementById("legend")) {

        document.getElementById("legend").remove();

    }

    $('#data-selector-form').on('change', function (e) {

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
                        year: $('#year-selector').val(),
                        nationality: $('input[name=nationality]:checked').val(),
                        gender: $("input[name=gender]:checked").val()
                    },
                    type: 'POST',
                    url: '/mapupdate/'
                })
                    .done(function (data, statusText, xhr) {
                        console.log(data.table[0]);
                        $('#ws').text("Wintersemester "+data.year+', '+data.nationality+', '+data.gender);
                        let $map = $('#folium-map').contents().clone();
                        let $new_map = $(data.map);
                        // //TODO: Optimize map include
                        // let map_name = $("div[id*='map_']").get(0).id;
                        // let map = window[map_name];
                        //
                        // let gj = JSON.parse(data.geojson);
                        // console.log(gj);

                        // L.geoJSON(gj).addTo(map);
                        //map.addLayer(gj);
                        $('#folium-map').empty();
                        $('#folium-map').append('<div id = \'custom-legend\'></div>');
                        $('#folium-map').append($new_map);

                        let table = data.table;
                        let pop = $('.population');
                        let studAbs = $('.students_a');
                        let studRel = $('.students_r');

                        for (var i = 0; i < 16; i++){
                            pop[i].textContent = numeral(table[i][1]).format('0,0');
                            studAbs[i].textContent = numeral(table[i][2]).format('0,0');
                            studRel[i].textContent = numeral(table[i][2]/table[i][1]).format('0.00%');
                        }
                    });
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
                        $('#folium-map').append('<div id = \'custom-legend\'></div>');
                        $('#folium-map').append($new_map);

                        $('#legend').remove();

                        $('#state-hzb').text(data.state);
                        let table = data.table;
                        let total = data.total;
                        let bins = data.bins;
                        console.log(bins);
                        let studAbs = $('.students_a');
                        let studRel = $('.students_r');

                        var binBox = document.createElement('div');
                        binBox.id = 'bin-box';
                        $('#custom-legend').append(binBox);
                        for (i = 0; i < 5; i++) {
                            var bin = document.createElement('div');
                            var label = document.createElement('p');
                            label.innerText = bins[i];
                            bin.id = 'bin' + i;
                            bin.appendChild(label);
                            binBox.appendChild(bin);
                        }

                        var label = document.createElement('p');
                        label.innerText = bins[5];
                        document.getElementById('bin4').appendChild(label);

                        for (var i = 0; i < 16; i++){
                            studAbs[i].textContent = numeral(table[i][1]).format('0,0');
                            studRel[i].textContent = numeral(table[i][1]/total).format('0.00%');
                        }

                        $.ajax({
                            type: 'GET',
                            url: '/bokeh_data_place_of_study/?year=' + encodeURIComponent(data.year) + '&state=' + encodeURIComponent(data.state)
                            + '&gender=' + encodeURIComponent(data.gender)
                        })
                            .done(function (data) {

                                let ds = Bokeh.documents[0].get_model_by_name('place-of-study');
                                console.log(ds);
                                ds.data = data.source.data;
                                console.log(data.source.data);
                                console.log(ds.data.männlich);
                                ds.document.layoutables[0].x_range.end = Math.max(...ds.data.counts);
                                ds.change.emit();

                                /*
                                ds.document.layoutables[0].x_range.start=0
                                ds.document.layoutables[0].x_range.end=200000
                                 */
                            })

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
                ds.change.emit();

                let currentYear = $('#year-slider-uni').find('output#slider-value').val();
                let tableData = data.table;
                let uniAll = 0, hsAll = 0, kmhAll = 0, otherAll = 0, resultAll = 0;

                let uni = tableData[currentYear].uni;
                let hs = tableData[currentYear].hs;
                let kmh = tableData[currentYear].kmh;
                let other = tableData[currentYear].other;
                let result = uni+hs+kmh+other;
                //console.log(currentYear);

                $('#uni-year').text(currentYear);
                $('#uni').text(uni);
                $('#hs').text(hs);
                $('#kmh').text(kmh);
                $('#other').text(other);
                $('#result-year').text(result);

                for (let year in tableData){

                    if ( year <= currentYear){
                        // console.log("year:" + year, "currentYear: "+currentYear);
                        uniAll += tableData[year].uni;
                        hsAll += tableData[year].hs;
                        kmhAll += tableData[year].kmh;
                        otherAll += tableData[year].other;
                        resultAll = uniAll+hsAll+kmhAll+otherAll;
                    }
                }
                $('#uni-all').text(uniAll);
                $('#hs-all').text(hsAll);
                $('#kmh-all').text(kmhAll);
                $('#other-all').text(otherAll);
                $('#result-all').text(resultAll);

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



