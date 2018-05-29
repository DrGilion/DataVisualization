var countries;
var country_to_cc;
var categories;

var default_category = "Total";
var default_dimension = "totals";

var current_cc;
var current_category;
var current_year;
var current_dimension;

var current_aggregates;
var current_data;

$(document).on("charts_drawn", function () {
    $("#charts").LoadingOverlay("hide");
});

function request_chart_redraw() {
    $("#charts").LoadingOverlay("show");
    $( document ).trigger( "draw_charts" );
}

function get_dimension() {
    return $("#Dimension").val();
}

function get_current_years() {
    var years = countries[current_cc]["years"][current_category];
    return years;
}

function get_current_categories() {
    var categories = new Set();

    for(let category in countries[current_cc]["years"]) {
        if(countries[current_cc]["years"][category].includes(current_year)) {
            categories.add(category);
        }
    }

    var lCategories = [];
    for(let cat of categories) {
        lCategories.push(cat);
    }
    lCategories.sort();

    return lCategories;
}

function selection_update() {
    _selection_update(current_cc, $("#Years").val(), $("#ProductCategory").val(), $("#Dimension").val());
}

function _selection_update(cc, year, category, dimension) {
    disable_inputs();

    // get data
    var aggregate_url = "/vis_data/aggregate_"+cc.toLowerCase()+".json";
    var data_url = "/vis_data/partners_"+cc.toLowerCase()+"_"+year+"_"+category.toLowerCase()+".json";


    current_cc = cc;
    current_category = category;
    current_year = year;
    current_dimension = dimension;

    $.when( $.getJSON( aggregate_url ), $.getJSON( data_url ) ).done(function( _aggregates, _data ) {
        current_aggregates = _aggregates[0];
        current_data = _data[0];

        init_years();
        init_categories();
        enable_inputs();
        request_chart_redraw();
    });
}

function disable_inputs() {
    $("#Country").prop('disabled', true);
    $("#Years").prop('disabled', true);
    $("#ProductCategory").prop('disabled', true);
    $("#Dimension").prop('disabled', true);
}

function enable_inputs() {
    $("#Country").prop('disabled', false);
    $("#Years").prop('disabled', false);
    $("#ProductCategory").prop('disabled', false);
    $("#Dimension").prop('disabled', false);
}

function country_selected(cc) {
    var last_index = countries[cc]["years"][default_category].length - 1;
    var latest_year = countries[cc]["years"][default_category][last_index];
    $("#Dimension").val(default_dimension);
    _selection_update(cc, latest_year, default_category, default_dimension);
}

function init_autocomplete() {
    var country_list = [];

    $.each(countries, function(key, value) {
        country_list.push(value["full_name"]);
    });

    autocomplete(document.getElementById("Country"), country_list, function(selection) {
        var cc = country_to_cc[selection];
        country_selected(cc);
    });
}

function init_years() {
    if (typeof(current_data) === 'undefined') {
        $("#Years").prop('disabled', true);
        return;
    }

    var years = get_current_years();

    var inp = $("#Years");
    inp.empty();
    $.each(years, function(index, value) {
        inp.append($("<option></option>")
            .attr("value", value).text(value));
    });
    inp.prop('disabled', false);

    if(!years.includes(current_year)) {
        current_year = years[years.length-1];
    }
    inp.val(current_year);
}

function init_categories() {
    if (typeof(current_data) === 'undefined') {
        $("#ProductCategory").prop('disabled', true);
        return;
    }

    var categories = get_current_categories();

    var inp = $("#ProductCategory");
    inp.empty();
    $.each(categories, function(index, value) {
        inp.append($("<option></option>")
            .attr("value", value).text(value));
    });
    inp.prop('disabled', false);

    if(!categories.includes(current_category)) {
        current_category = default_category;
    }
    inp.val(current_category);
}


function loadBaseData(cb) {
    $.when( $.getJSON( "/vis_data/countries.json" ), $.getJSON( "/vis_data/categories.json" ) ).done(function( _countries, _categories ) {
        if(_countries[2]["status"] !== 200 || _categories[2]["status"] !== 200) {
            alert("Failed to load base data!");
            debugger;
        }

        country_to_cc = {};
        countries = _countries[0];
        $.each(countries, function(key, value) {
            country_to_cc[value["full_name"]] = key;
        });
        categories = _categories[0];
        cb();
    });
}

function init() {
    $.LoadingOverlay("show");
    loadBaseData(function () {
        init_autocomplete();
        init_years();
        init_categories();

        $("#Years").change(function() {
            selection_update();
        });
        $("#ProductCategory").change(function() {
            selection_update();
        });
        $("#Dimension").change(function() {
            selection_update();
        });

        $.LoadingOverlay("hide");
    });
}

$( document ).ready(function() {
    init();
});