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

function drawPieChart() {
    var area = $("#pieChart");
    area.html("<div class='todo'>TODO!</div>");
}

function drawLineChart() {
    var area = $("#lineChart");
    area.html("<div class='todo'>TODO!</div>");
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

    $.each(resourceColorTable, function(key, color) {
        var category = categories[key];
        legendContainer.append("<div class='label'><div class='color' style='background: "+color+"'>&nbsp;</div> "+category+"</div>");
    });

    legend.append(legendContainer);
}


$(document).on("draw_charts", function () {
    drawLegend();
    drawPieChart();
    drawLineChart();
    drawGeoChart();
    drawTreeMapChart();
    $(document).trigger("charts_drawn");
});