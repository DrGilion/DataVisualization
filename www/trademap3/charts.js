var resourceColorTable = {
    '84-85_MachElec':'#ccbb55',
    'manuf':'#66aa00',
    '06-15_Vegetable':'#ff9900',
    'AgrRaw':'#3366cc',
    '41-43_HidesSkin':'#b82e2e',
    '90-99_Miscellan':'#33ff11',
    'Fuels':'#e31b23',
    'UNCTAD-SoP1':'#666622',
    'Textiles':'#b77322',
    '27-27_Fuels':'#f4359e',
    'OresMtls':'#00ddff',
    '25-26_Minerals':'#109618',
    '68-71_StoneGlas':'#22aa99',
    '39-40_PlastiRub':'#336677',
    'UNCTAD-SoP3':'#ffee11',
    '44-49_Wood':'#ff8833',
    '28-38_Chemicals':'#333333',
    'UNCTAD-SoP4':'#668811',
    '50-63_TextCloth':'#66cc11',
    'Food':'#0099bb',
    'UNCTAD-SoP2':'#d32e2e',
    'Transp':'#dc3912',
    '16-24_FoodProd':'#330011',
    '01-05_Animal':'#994499',
    '86-89_Transport':'#9977bb',
    'Chemical':'#6600bb',
    '64-67_Footwear':'#990033',
    '72-83_Metals':'#6699cc'
};
var usedLabels;

function getFirstItemsByVal(dict, num) {
    var items = Object.keys(dict).map(function(key) {
        return [key, dict[key]];
    });

    items.sort(function(first, second) {
        return second[1] - first[1];
    });

    return items.slice(0, num);
}

function addToCategories(catArr, arr) {
    $.each(arr, function(key, value) {
        // ignore default category
        if (value["id"] === default_category) {
            return;
        }

        if(!(value["id"] in catArr)) {
            catArr[value["id"]] = 0;
        }

        catArr[value["id"]] += value["percent"];
    });
}

function drawPieChart() {
    // generate data
    var relObj = current_aggregates["years"].find(x => x["year"] === current_year);

    var allCategories = {};
    if(current_dimension === "exports" || current_dimension === "totals") {
        addToCategories(allCategories, relObj["exports"]);
    }

    if(current_dimension === "imports" || current_dimension === "totals") {
        addToCategories(allCategories, relObj["imports"]);
    }

    var config = {
        type: 'pie',
        data: {
            datasets: [{
                data: [
                ],
                backgroundColor: [
                ]
            }],
            labels: [
            ]
        },
        options: {
            responsive: true,
            legend: {
                display: false,
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        var label = data.labels[tooltipItem.index] || '';
                        if (label) {
                            label += ': ';
                            label += data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                            label += ' %';
                        }
                        return label;
                    }
                }
            }
        }
    };

    var total_percent = 0;
    var displayCategories = getFirstItemsByVal(allCategories, 8);
    $.each(displayCategories, function(key, value) {
        var catId = value[0];
        var percent = value[1];
        if(current_dimension === "totals") {
            percent = percent * 0.5;
            percent = Math.round(percent, 2);
        }
        total_percent += percent;

        usedLabels.add(catId);

        config.data.datasets[0].data.push(percent);
        config.data.datasets[0].backgroundColor.push(resourceColorTable[catId]);
        config.data.labels.push(categories[catId]);
    });

    // add others
    config.data.datasets[0].data.push((100-total_percent));
    config.data.datasets[0].backgroundColor.push(resourceColorTable["others"]);
    config.data.labels.push(categories["others"]);
    usedLabels.add("others");

    var area = $("#pieChart");
    area.empty();

    var canvas = $("<canvas>");
    area.append(canvas);

    var ctx = canvas[0].getContext('2d');
    window.myPie = new Chart(ctx, config);
}

function drawLineChart() {
    // generate data
    var allCategories = {};

    var years = [];
    $.each(current_aggregates["years"], function(key, value) {
       if(current_dimension === "exports" || current_dimension === "totals") {
           addToCategories(allCategories, value["exports"]);
       }

        if(current_dimension === "imports" || current_dimension === "totals") {
            addToCategories(allCategories, value["imports"]);
        }

        years.push(value["year"]);
    });
    years.sort();


    var config = {
        type: 'line',
        data: {
            labels: years,
            datasets: []
        },
        options: {
            responsive: true,
            legend: {
                display: false,
            },
            title: {
                display: false
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        var label = data.datasets[tooltipItem.datasetIndex].label || '';
                        if (label) {
                            label += ': ';
                            label += data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                            label += ' %';
                        }
                        return label;
                    }
                }
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: false,
                        labelString: 'Year'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Percent'
                    }
                }]
            }
        }
    };

    var displayCategories = getFirstItemsByVal(allCategories, 8);
    $.each(displayCategories, function(key, value) {
        var catId = value[0];
        usedLabels.add(catId);

        var dataset = {
            label: categories[catId],
            backgroundColor: resourceColorTable[catId],
            borderColor: resourceColorTable[catId],
            data: [
            ],
            fill: false,
        };
        for(var year of years) {
            var dat = current_aggregates["years"].find(x => x["year"] === year);
            var percent = 0;

            var added = 0;
            if(current_dimension === "exports" || current_dimension === "totals") {
                var obj = dat["exports"].find(x => x["id"] === catId);
                if(typeof obj !== 'undefined') {
                    percent += obj["percent"];
                    added += 1;
                }
            }

            if(current_dimension === "imports" || current_dimension === "totals") {
                var obj = dat["imports"].find(x => x["id"] === catId);
                if(typeof obj !== 'undefined') {
                    percent += obj["percent"];
                    added += 1;
                }
            }

            if(percent > 0) {
                percent = percent/added;
                percent = Math.round(percent, 2);
            }

            dataset.data.push(percent);
        }
        config.data.datasets.push(dataset);
    });

    var area = $("#lineChart");
    area.empty();

    var canvas = $("<canvas>");
    area.append(canvas);

    var ctx = canvas[0].getContext('2d');
    window.myLine = new Chart(ctx, config);
}

function drawGeoChart() {
    var area = $("#geoChart");
    area.empty();

    var chartData = {
        title: {
            text: null
        },
        chart: {
            borderWidth: 0,
            map: 'custom/world'
        },
        colorAxis: {
            min: -100,
            stops: [
                [0, '#FF0000'],
                [0.5, '#EEEEEE'],
                [1, '#00FF00']
            ]
        },
        mapNavigation: {
            enabled: true
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'bottom'
        },
        series: [{
            data: [
            ],
            name: 'Trading volume',
            states: {
                hover: {
                    color: Highcharts.getOptions().colors[2],
                    borderWidth: 1
                }
            },
            borderColor: 'black',
            borderWidth: 0.2,
            joinBy: ['iso-a3','hc-key'],
            dataLabels: {
                enabled: false
            },
            tooltip: {
                /*pointFormat: '<b><u>{point.name}:</u></b><br>Imports: ${point.imports}<br>Exports: ${point.exports}'*/
                pointFormatter: function(){
                    if(this.options.imports){
                        return '<b><u>' + this.name + ':</u></b><br>Imports: $' + this.options.imports  + '<br>Exports: $' + this.options.exports;
                    }else{
                        return 'Current Country (' + this.name + ')';
                    }
                }
            }
        }]
    };


    var partner_ccs = new Set();
    $.each(current_data, function(key, value) {
        $.each(value, function(index, data) {
            partner_ccs.add(data["cc"]);
        });
    });


    for (var cc of partner_ccs){
        var expSum = current_data["exports"].find(x => x["cc"] == cc);
        var impSum = current_data["imports"].find(x => x["cc"] == cc);

        var ratio = 0;

        if(typeof expSum === 'undefined' && typeof impSum === 'undefined') {
            continue;
        } else if (typeof expSum === 'undefined') {
            // nur importe
            ratio = -100;
        } else if (typeof impSum === 'undefined') {
            // nur exporte
            ratio = 100;
        } else  {
            expSum = expSum["amount"];
            impSum = impSum["amount"];

            var total = expSum+impSum;
            if(expSum > impSum) {
                ratio = (expSum/total)*100;
            } else {
                ratio = (impSum/total)*100*-1;
            }
        }

        var _imports = 0;
        var _exports = 0;
        if(typeof impSum !== "undefined") {
            _imports = Math.round(impSum, 2)*1000;
        }
        if(typeof expSum !== "undefined") {
            _exports = Math.round(expSum, 2)*1000;
        }

        chartData.series[0].data.push({
            "hc-key" : cc,
            "value": ratio,
            "imports": _imports,
            "exports": _exports
        });
    }


    chartData.series[0].data.push({
        "hc-key": current_cc,
        "color":"blue"
    });

    Highcharts.mapChart('geoChart', chartData);
}

function drawTreeMapChart() {
    var area = $("#treeMapChart");
    area.empty();


    var chart = {
        chart: {
            margin:  [0,0,0,0]
        },
        series: [{
            type: "treemap",
            layoutAlgorithm: 'squarified',
            data: []
        }],
        title: {
            text: null
        },
        tooltip: {
            formatter: function(){
                return '<strong>' + this.point.name + '</strong>: $ ' + Math.floor(this.point.value * 1000);
            }
        }
    };

    var cData = {};
    $.each(current_data, function(key, value) {
        if(current_dimension === key || current_dimension === "totals") {
            $.each(value, function (key, value) {
                if(!(value["cc"] in cData)) {
                    cData[value["cc"]] = 0;
                }

                cData[value["cc"]] += value["amount"];
            });
        }
    });

    for (cc in cData) {
        chart.series[0].data.push({
            name: countries[cc]["full_name"],
            value: cData[cc]
        });
    }

    Highcharts.chart('treeMapChart', chart);

    var title = $("#treeMapTitle");

    if(current_dimension === "totals")
        title.text("Absolute Trade Amounts");
    if(current_dimension === "exports")
        title.text("Largest Export Partners");
    if(current_dimension === "imports")
        title.text("Largest Import Partners");
}

function drawLegend() {
    var legend = $("#legend");
    legend.empty();

    var legendContainer = $("<div>");
    legendContainer.addClass("legendContainer");

    /*
    $.each(resourceColorTable, function(key, color) {
        var category = categories[key];
        legendContainer.append("<div class='label'><div class='color' style='background: "+color+"'>&nbsp;</div> "+category+"</div>");
    });
    */

    // Nur die Labels, die wir auch anzeigen!
    for(var lbl of usedLabels.entries()) {
        var catId = lbl[0];
        var category = categories[catId];
        var color = resourceColorTable[catId];
        legendContainer.append("<div class='label'><div class='color' style='background: "+color+"'>&nbsp;</div> "+category+"</div>");
    }

    legend.append(legendContainer);
}


$(document).on("draw_charts", function () {
    usedLabels = new Set();


    drawPieChart();
    drawLineChart();
    drawGeoChart();
    drawTreeMapChart();
    drawLegend();

    $(document).trigger("charts_drawn");
});

$(document).on("initialized", function() {
    // monkeypatch
    categories["others"] = "Others";
    resourceColorTable["others"] = "#cccccc";
});
