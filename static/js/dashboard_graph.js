$(document).ready(function() {

// var wan;
    Highcharts.setOptions({
                global: {
                    useUTC: false
                   
                }
            });

    function draw_chart(usage_range,chart_type) {
        // alert(usage_range);
    var url="controller/dashboard.php?action=usage_graph&usage_range="+usage_range;
    $.getJSON(url,
        function(data1){
            // var download = data1.download;
            // var data2 = JSON.parse(e.data);
            // console.log(data1.download);
            // var temp = [3459898435, 435782, 4352, 243524853, 43878324578723457, 3457273];

    options = {
        chart: {

                    alignTicks: true,
                    animation: true,
                    backgroundColor: "#FFFFFF",
                    borderColor: "#335cad",
                    borderRadius: 0,
                    borderWidth: 0,
                    colorCount: 10,
                    // defaultSeriesType: "column",
                    //  events: {

                    //     load: function () {

                            

                                

                    //          var action = $('#usage_range :selected').val();
                    //          var graph = this;
                    //          getdata(graph,action);
                    //           $('#usage_range').on('change', function() {
                    //             var action = this.value;
                    //             getdata(graph,action);
                    //           });
                    //     }
                    // },
                    height: null,
                    ignoreHiddenSeries: true,
                    inverted: false,
                    panning: true,
                    pinchType: null,
                    plotBorderColor: "#cccccc",
                    plotBorderWidth: 0,
                    plotShadow: true,
                    polar: true,
                    reflow: true,
                    renderTo: 'usage_graph',
                    selectionMarkerFill: "rgba(51,92,173,0.25)",
                    shadow: true,
                    showAxes: true,
                    spacing: [10, 10, 15, 10],
                    spacingBottom: 15,
                    spacingLeft: 10,
                    spacingRight: 10,
                    spacingTop: 10,
                    style: {"fontFamily":"\"Lucida Grande\", \"Lucida Sans Unicode\", Verdana, Arial, Helvetica, sans-serif","fontSize":"12px"},
                    type: "area",
                    // height: 340
                    },
        title: {
            text: 'DATA Usage'
        },
        credits:{
                    enabled: false
                },
        
        xAxis: {
            type: 'datetime',
              dateTimeLabelFormats: {
            month: '%e. %b',
            year: '%b'
        },
            title: {
                text: 'Date'
            },

        },
        yAxis: {
            enabled: true,
            labels: {
            formatter: function() { return bytes(this.value, true); }
             },
            title: {
                text: 'Total Data'
            },
            floor: 0,
            allowDecimals: true

        },
        tooltip: {
        enabled: true,
        formatter: function() { return bytes(this.y, true);}
        },
        legend: {
            enabled: true
        },
        plotOptions: {
            area: {
                fillColor: {
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    stops: [
                        [0, Highcharts.getOptions().colors[0]],
                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                    ]
                },
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 3
                    }
                }
                
            }
        },

        series: [{
            type: chart_type,
            name: 'TotalData('+ usage_range +')',
            data: [],
        },{
            type: chart_type,
            name: 'DownData('+ usage_range +')',
            data: [],
        },{
            type: chart_type,
            name: 'UpData('+ usage_range +')',
            data: [],
        }]
        }
        
        // options.xAxis.categories = data1.date_org;
        options.series[0].data = data1.data;
        options.series[1].data = data1.download;
        options.series[2].data = data1.upload;
        
        // options.series[1].data = [data1.date,data1.download];
        // options.series[1].data = [data1.date,data1.download];

        // console.log(data1.date_org);
        var chart = new Highcharts.Chart(options);


    });

    }

   var usage_range = $('#usage_range :selected').val();
   var chart_type = $('#chart_type :selected').val();
   

  

   $('#chart_type').on('change', function() {
    chart_type = this.value;
    draw_chart(usage_range,chart_type);
  });

   $('#usage_range').on('change', function() {
    usage_range = this.value;
    draw_chart(usage_range,chart_type);
  });

   draw_chart(usage_range,chart_type);
   delete usage_range,chart_type;




});

    function bytes(bytes, label) {
    if (bytes == 0) return '';
    var s = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
    var e = Math.floor(Math.log(bytes)/Math.log(1024));
    var value = ((bytes/Math.pow(1024, Math.floor(e))).toFixed(0));
    e = (e<0) ? (-e) : e;
    if (label) value += ' ' + s[e];
    return value;

    }