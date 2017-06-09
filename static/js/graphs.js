/**
 * Created by dobro on 17. 5. 18.
 */
queue()
    .defer(d3.json, "./data")
    .await(makeDashBoard);

function makeDashBoard(error, recordsJson) {
    var records = recordsJson;
    var dateFormat = d3.time.format("%m/%d/%Y");
    records.forEach(function (d) {
        d["date"] = dateFormat.parse(d["date"]);
    });

    var ndx = crossfilter(records);

    var dateDim = ndx.dimension(function (d) { return d["date"]; });
    var authorDim = ndx.dimension(function (d) { return d["author"]; });

    var moodDim = ndx.dimension(function (d) { return d["mood"]; });
    var moodPerDim = ndx.dimension(function (d) { return d["mood"]; });

    var genreDim = ndx.dimension(function (d) { return d["genre"]; });
    var genrePerDim = ndx.dimension(function (d) { return d["genre"]; });

    var allDim = ndx.dimension(function(d) {return d;});

    var numRecordsByDate = dateDim.group();
    var moodGroup = moodDim.group();
    var genreGroup = genreDim.group();
    var authorGroup = authorDim.group();
    var all = ndx.groupAll();



    function reduceAddAvg(attr) {
        return function(p,v) {
            ++p.count;
            p.sums += v[attr];
            p.averages = (p.count === 0) ? 0 : p.sums/p.count; // gaurd against dividing by zero
            return p;
        };
    }
    function reduceRemoveAvg(attr) {
        return function(p,v) {
            --p.count;
            p.sums -= v[attr];
            p.averages = (p.count === 0) ? 0 : p.sums/p.count;
            return p;
        };
    }
    function reduceInitAvg() {
        return {count:0, sums:0, averages:0};
    }


    var genrePerLenGroup = genrePerDim.group().reduce(reduceAddAvg("Length"), reduceRemoveAvg("Length"), reduceInitAvg);

    var moodPerLenGroup = moodPerDim.group().reduce(reduceAddAvg("Length"), reduceRemoveAvg("Length"), reduceInitAvg);


    var minDate = dateDim.bottom(1)[0]["date"];
    var maxDate = dateDim.top(1)[0]["date"];

    var numberRecordsND = dc.numberDisplay("#number-records-nd");
    var timeWidth = document.getElementById('chart1').offsetWidth;
    var timeChart = dc.barChart("#time-chart");
    numberRecordsND
        .formatNumber(d3.format("d"))
        .valueAccessor(function(d){ return d; })
        .group(all);
    timeChart
        .width(timeWidth)
        .height(140)
        .margins({top: 10, right: 50, bottom: 20, left: 20})
        .dimension(dateDim)
        .group(numRecordsByDate)
        .mouseZoomable(true)
        .transitionDuration(500)
        .x(d3.time.scale().domain([minDate, maxDate]))
        .elasticY(true)
        .yAxis().ticks(4);

    /* mood Chart - histogram */
    var moodWidth = document.getElementById('chart2').offsetWidth;
    var moodChart = dc.rowChart("#mood-row-chart");
    moodChart
        .width(moodWidth)
        .height(310)
        .dimension(moodDim)
        .group(moodGroup)
        .ordering(function(d) { return -d.value })
        .ordinalColors(['#3182bd', '#6baed6', '#9ecae1', '#c6dbef', '#dadaeb'])
        .elasticX(true)
        .xAxis().ticks(4);

    /*genre chart pie Chart*/
    var genreWidth = document.getElementById('chart3').offsetWidth;
    var genreChart = dc.pieChart("#genre-pie-chart");
    genreChart
        .width(genreWidth)
        .height(310)
        .radius(150)
        .innerRadius(50)
        .dimension(genreDim)
        .colors(d3.scale.category20c())
        .group(genreGroup);

    /*Author Chart horizon bar chart*/
    var authorWidth = document.getElementById('chart4').offsetWidth;
    var AuthorChart = dc.rowChart("#top10-row-chart");
    AuthorChart
        .width(authorWidth)
        .height(510)
        .dimension(authorDim)
        .group(authorGroup)
        .data(function (group) { return group.top(10);})
        .ordering(function(d) { return -d.value })
        .transitionDuration(500)
        .elasticX(true)
        .xAxis().ticks(4);

    /*Music Length Histogram*/
    var gLengthWidth = document.getElementById('chart5').offsetWidth;
    var gLengthChart = dc.barChart("#genre-length-chart")
        .xAxisLabel('장르')
        .yAxisLabel('평균 길이(초)');

    gLengthChart
        .width(gLengthWidth)
        .height(185)
        .dimension(genrePerDim)
        .group(genrePerLenGroup)
        .valueAccessor(function (p) {
            return p.value.averages;
        })
        .elasticY(true)
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .colors(["orange"])
        .yAxis().ticks(5);

    /*Music Length Histogram*/
    var mLengthWidth = document.getElementById('chart5').offsetWidth;
    var mLengthChart = dc.barChart("#mood-length-chart")
        .xAxisLabel('분위기')
        .yAxisLabel('평균 길이(초)');

    mLengthChart
        .width(mLengthWidth)
        .height(185)
        .dimension(moodPerDim)
        .group(moodPerLenGroup)
        .valueAccessor(function (p) {
            return p.value.averages;
        })
        .elasticY(true)
        .x(d3.scale.ordinal())
        .xUnits(dc.units.ordinal)
        .colors(["orange"])
        .yAxis().ticks(5);


    /*chart draw*/
    dcCharts = [timeChart, moodChart, genreChart, AuthorChart, gLengthChart, mLengthChart];

    _.each(dcCharts, function (dcChart) {
        dcChart.on("filtered", function (chart, filter) {
        });
    });

    dc.renderAll();
}