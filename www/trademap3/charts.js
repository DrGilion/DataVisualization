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
                ],
                label: 'Dataset'
            }],
            labels: [
            ]
        },
        options: {
            responsive: true,
            legend: {
                display: false,
            },
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
                mode: 'index',
                intersect: false,
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
    area.html("<div class='todo'>TODO!</div>");
}

function drawTreeMapChart() {
    var area = $("#treeMapChart");
    area.html("<div class='todo'>TODO!</div>");
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