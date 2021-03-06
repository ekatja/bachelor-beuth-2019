$(document).ready(function () {

    // Remove default legend for replace with custom legend
    if (document.getElementById("legend")) {
        document.getElementById("legend").remove();
    }

    // Navigate to corresponding page according to selected dataset
    $('#data-selector-form').on('change', function (e) {

        switch ($('#data-selector').val()) {
            case 'st_bd': {
                window.location = "/map/";
                break;
            }
            case 'university-foundation-year': {
                window.location = "/university-foundation-year/";
                break;
            }
            case 'place-of-study': {
                window.location = "/place-of-study/";
                break;
            }
        }
        e.preventDefault();
    });

    // Request data according to current page and selected options
    $('#options-selector-form').on('change', function (e) {

        switch(window.location.pathname){
            case '/map/': {
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
                    .done(function (data) {
                        // Set page title
                        $('#ws').text("Wintersemester " + data.year + ', ' + data.nationality + ', ' + data.gender);

                        // Update map
                        let new_map = $(data.map);
                        $('#folium-map').empty().append(new_map).append('<div id = \'custom-legend\'></div>');
                        $('#legend').remove();

                        // Update legend
                        let bins = data.bins;
                        createLegend(bins);

                        // Update table data
                        let table = data.table;
                        let pop = $('.population');
                        let studAbs = $('.students_a');
                        let studRel = $('.students_r');

                        for (var i = 0; i < 16; i++) {
                            pop[i].textContent = numeral(table[i][1]).format('0,0');
                            studAbs[i].textContent = numeral(table[i][2]).format('0,0');
                            studRel[i].textContent = numeral(table[i][2] / table[i][1]).format('0.00%');
                        }
                    });
                break;
            }
            case '/place-of-study/':{
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
                        // Update page title
                        $('#ws').text("Wintersemester "+data.year+', '+data.state+', '+data.gender);

                        // Update map
                        let map = $('#folium-map').contents().clone();
                        let new_map = $(data.map);
                        //TODO: Optimize map include
                        $('#folium-map').empty();
                        $('#folium-map').append('<div id = \'custom-legend\'></div>');
                        $('#folium-map').append(new_map);
                        $('#legend').remove();

                        // Update map legend
                        let bins = data.bins;
                        createLegend(bins);

                        $('#state-hzb').text(data.state);
                        let table = data.table;
                        let total = data.total;
                        let studAbs = $('.students_a');
                        let studRel = $('.students_r');

                        for (var i = 0; i < 16; i++){
                            studAbs[i].textContent = numeral(table[i][1]).format('0,0');
                            studRel[i].textContent = numeral(table[i][1]/total).format('0.00%');
                        }

                        // Send selected options to backend for chart update
                        $.ajax({
                            type: 'GET',
                            url: '/bokeh_data_place_of_study/?year=' + encodeURIComponent(data.year) + '&state=' + encodeURIComponent(data.state)
                            + '&gender=' + encodeURIComponent(data.gender)
                        })
                            .done(function (data) {

                                let ds = Bokeh.documents[0].get_model_by_name('place-of-study');
                                ds.data = data.source.data;
                                ds.document.layoutables[0].x_range.end = Math.max(...ds.data.counts);
                                ds.change.emit();
                            });
                    });
                break;
            }
            e.preventDefault();
        }
    });

    // Request line chart and table update for the selected year for university-by-year visualization
    $('#year-slider-uni').on('change', function (e) {

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

                // Update table data
                let uni = tableData[currentYear].uni;
                let hs = tableData[currentYear].hs;
                let kmh = tableData[currentYear].kmh;
                let other = tableData[currentYear].other;
                let result = uni+hs+kmh+other;

                $('#uni-year').text(currentYear);
                $('#uni').text(uni);
                $('#hs').text(hs);
                $('#kmh').text(kmh);
                $('#other').text(other);
                $('#result-year').text(result);

                for (let year in tableData){

                    if ( year <= currentYear){
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

        e.preventDefault();
    });

    // Toggle extra information overlay panel
    $('.btn-showinfo').click(function () {
        $('.statistic-content').toggleClass('open-info');
        $(this).find('i').toggleClass('fa-angle-up fa-angle-down');
    });

});

/**
 * Create custom map legend
 * @param binsArr - array with bins ranges
 */
function createLegend(binsArr) {
    var binBox = document.createElement('div');
    binBox.id = 'bin-box';
    $('#custom-legend').append(binBox);

    for (i = 0; i < binsArr.length - 1; i++) {
        var bin = document.createElement('div');
        var label = document.createElement('p');
        label.innerText = binsArr[i];
        bin.id = 'bin' + i;
        bin.appendChild(label);
        binBox.appendChild(bin);
    }
    var label = document.createElement('p');
    label.innerText = binsArr[binsArr.length - 1];
    document.getElementById('bin' + String(binsArr.length - 2)).appendChild(label);
}