function draw(geo_data) {

    // Create Title
    var title = d3.select('header')
        .append('h1')
        .text('50 Years of Mass Shootings in America: 1968-2017');

    // SVG Size
    var width = 1100;
    var height = 450;

    // GeoGSON Projection -> USA by State
    var projection = d3.geo.albersUsa()
        .translate([width / 2, height / 2])    // center map to the SVG
        .scale([900]);          		       // zoom

    // GeoJSON to SVG Path
    var path = d3.geo.path()
        .projection(projection);

    //Define colors to sort shootings by State into color buckets
    //Colors chosen from colorbrewer.js
    var color = d3.scale.threshold() // threshold lets us specify the values splitting categories.
        .range(['rgb(245, 245, 245)', 'rgb(255,255,178)', 'rgb(254,204,92)', 'rgb(253,141,60)', 'rgb(227,26,28)'])
        .domain([0, 3, 6, 10]); // values between categories. Always (n-1) color buckets.

    //Define colors to sort circles by decade when shootings happened
    var circlecolor = d3.scale.threshold()
        .range(['rgb(217,217,217)', 'rgb(189,189,189)', 'rgb(150,150,150)', 'rgb(99,99,99)', 'rgb(37,37,37)'])
        .domain([1978, 1988, 1998, 2008]); // split the shootings into decades.

    //Create Map SVG element
    var svg = d3.select('section')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('class', 'map');
    



    // Create year evolution text. Here called 'subtitle'
    var subtitle = d3.select('section').append('svg')
        .attr('class', 'subtitle')
        .attr('width', 160)
        .attr('height', 100);


    /*
    Note on legend: as threshold domain has (n-1) variables as color range
    and these are passed into color & circlecolor legends, it was necessary to create an extra
    unexistant color domain ('-1'), or else the legends would have 1 missing category.
    */

    // First legend: States color scheme
    var legendText = ['None', 'From 1 to 3', 'From 3 to 5', 'From 6 to 9', '10 or More'];
    var legend = d3.select('section').append('svg')
        .attr('class', 'legend')
        .attr('width', 160)
        .attr('height', 120)
        .selectAll('g')
        .data([-1, 0, 3, 6, 10]) //same as color.domain(), but with an extra category
        .enter()
        .append('g')
        .attr('transform', function (d, i) {
            return 'translate(0,' + i * 20 + ')';
        });

    legend.append('text')
        .data(['Shootings:'])
        .attr('class', 'legend_title')
        .attr('x', 10)
        .attr('y', 5)
        .attr('dy', '.35em')
        .text(function (d) {
            return d;
        });

    legend.append('rect')
        .attr('x', 10)
        .attr('y', 20)
        .attr('width', 18)
        .attr('height', 18)
        .style('fill', color);

    legend.append('text')
        .data(legendText)
        .attr('x', 35)
        .attr('y', 30)
        .attr('dy', '.35em')
        .text(function (d) {
            return d;
        });

    //Second legend: circles color scheme
    var circlelegendText = ['1968 - 1977', '1978 - 1987', 
    '1988 - 1997', '1998 - 2007', '2008 - 2017'];

    var circlelegend = d3.select('section').append('svg')
        .attr('class', 'circlelegend')
        .attr('width', 160)
        .attr('height', 120)
        .selectAll('g')
        .data([-1, 1978, 1988, 1998, 2008]) 
        //same as circlecolor.domain(), but with an extra category
        .enter()
        .append('g')
        .attr('transform', function (d, i) {
            return 'translate(0,' + i * 20 + ')';
        });

    circlelegend.append('text')
        .data(['Decade:'])
        .attr('class', 'legend_title')
        .attr('x', 10)
        .attr('y', 5)
        .attr('dy', '.35em')
        .text(function (d) {
            return d;
        });

    circlelegend.append('circle')
        .attr('cx', 18)
        .attr('cy', 27)
        .attr('r', 9)
        .style('fill', circlecolor)
        .style('opacity', 0.9);

    circlelegend.append('text')
        .data(circlelegendText)
        .attr('x', 32)
        .attr('y', 27)
        .attr('dy', '.35em')
        .text(function (d) {
            return d;
        });

    
    //Third legend: circle size
    //Code source: Mike Bostock (https://bost.ocks.org/mike/bubble-map/)
    var radius = d3.scale.sqrt()
        .domain([0, 600])
        .range([0, 70]);

    var circlesizelegend = svg.append('g')
        .attr('class', 'circlesizelegend')
        .attr('transform', 'translate(' + (width - 1050) + ',' + (height - 20) + ')')
        .selectAll('g')
        .data([200, 100, 50, 20])
        .enter().append('g');

    circlesizelegend.append('circle')
        .attr('cy', function (d) {
            return -radius(d);
        })
        .attr('r', radius);

    circlesizelegend.append('text')
        .attr('y', function (d) {
            return -2 * radius(d);
        })
        .attr('dy', '1.3em')
        .text(d3.format('.1s'));

    circlesizelegend.append('text')
        .data(['Victims Count'])
        .attr('x', 0)
        .attr('y', -100)
        .attr('dy', '.35em')
        .text(function (d) {
            return d;
        });


    // Tooltip: display pop-up data about shootingings on map.
    var div = d3.select('section')
        .append('div')
        .attr('class', 'tooltip');  

    // Years to iterate
    var years = [];
    for (var i = 1968; i < 2018; i++) {
        years.push(i);
    };

    //Bind path with GeoJSON feature
    //Color States according to var 'color'
    var map = svg.selectAll('path')
        .data(geo_data.features)
        .enter()
        .append('path')
        .attr('d', path)
        .style('stroke', 'black')
        .style('stroke-width', 0.5)
        .style('fill', 'rgb(245, 245, 245)');


    

    /* 
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    XXX PLOT_VALUES FUNCTION, WHERE THE MAGIC HAPPENS XXX
    XXXXXXXXXXXXXXXXX ONE YEAR AT A TIME XXXXXXXXXXXXXXXX
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    */


    function plot_values(data) { // DATA => SHOOTINGS.TSV

        function update(year) {

            subtitle.selectAll('text').remove();
            subtitle.append('text')
                .attr('class', 'subtitle_text')
                .attr('x', 5)
                .attr('y', 5)
                .attr('dy', '1em')
                .attr('font-size', 50)
                .attr('fill', 'grey')
                .text(year);
            

            // Accumulates the years 
            var filtered = data.filter(function (d) { return d.year <= year });
            

            // Group by State
            var nested = d3.nest()
                .key(function (d) { return d.state_name; }) // group by State
                .rollup(function (leaves) {
                    return {
                        'total_shootings': leaves.length
                    };
                })
                // origin of data, which goes through the key + rollup pipeline
                .entries(filtered); 
                

            //Load total shootings in GeoJSON data
            // First, filter the State name and the value to be loaded
            for (var i = 0; i < nested.length; i++) {
                var dataState = nested[i].key; // State name
                var dataValue = nested[i].values['total_shootings']; // Total shootings

                //Match with GeoJSON using State name as key
                //Copy (or replace previous) shooting information into GeoJSON file
                for (var j = 0; j < geo_data.features.length; j++) {
                    if (dataState == geo_data.features[j].properties.name) {
                        geo_data.features[j].properties.shootings = dataValue;
                        break;

                    }
                }
            }

            // Fill States shapes with colors according to accumulated shootings
            svg.selectAll('path')
                .transition()
                .duration(500)
                .style('fill', function (d) {
                    if (d.properties.shootings) {
                        return color(d.properties.shootings); // specifies the filling color
                    } 
                    // States with no shootings -> 'white smoke (gray 96)'
                    return 'rgb(245, 245, 245)'; 
                });
         
            // Plot each shooting event on map.
            // -> Circle color represents each decade when shootings happened.
            // -> Circle size represents total number of shooting victims.

            // remove all from previous year and draws again
            svg.selectAll('.mapcircles').remove(); 

            svg.append('g')
                .selectAll('circle')
                // filtered data includes all shootings up to that year (accumulated)
                .data(filtered) 
                .enter()
                .append('circle')
                .attr('class', 'mapcircles')
                .attr('cx', function (d) {
                    return projection([d.lon, d.lat])[0];
                })
                .attr('cy', function (d) {
                    return projection([d.lon, d.lat])[1];
                })
                .attr("r", function (d) {
                    return radius(d.total_victims);
                })
                .style('fill', function (d) {
                    return circlecolor(d.year);
                })
                .style('opacity', 0.9)
                //.style('stroke', 'blue')
                .style('stroke', 'grey')
                .style('stroke-width', 1)

                // Add onmouseover and onmouseout for tooltip.
                .on('mouseover', function (d) {
                    div.transition()
                        .duration(200)
                        .style('opacity', .9);
                    div.html('<strong>' + d.location + '</strong><br/>' +
                        d.date + '<br/>' +
                        'Total Victims: ' + d.total_victims + '<br/>' +
                        'Fatalities: ' + d.fatalities + '<br/>' +
                        'injuries: ' + d.injured
                    )
                        .style('left', (d3.event.pageX) + 'px')
                        .style('top', (d3.event.pageY - 28) + 'px');
                })
                .on('mouseout', function (d) {
                    div.transition()
                        .duration(500)
                        .style('opacity', 0);
                });


        }; // end of update function

        // Iterate through years
        var year_idx = 0;

        var year_interval = setInterval(function () {
            update(years[year_idx]); // run update function
            year_idx++; // asks for next year
            // runs until all years done. Clears year selection
            if (year_idx >= years.length) { 
                clearInterval(year_interval),
                subtitle.selectAll('text').remove();
                }
             }, 600); // 600ms interval

    } // end of plot_values function

    d3.tsv('shootings.tsv', function (d) { // loads shootings data to the map
        return d;
    }, plot_values);
    

}; // end of function draw(geo_data)

// run the draw frunction on the selected map.
d3.json('us-states.json', draw); 