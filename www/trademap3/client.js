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

/**
 * Loads for the selected country the available years
 * @returns {*} List of the years
 */
function get_current_years() {
    var years = countries[current_cc]["years"][current_category];
    return years;
}

/**
 * Loads for the selected country and selected year the available economy categories
 * @returns {Array} of the loading categories
 */
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

/**
 * Execution after an JQuery updates triggered by the dropdowns
 * wrapper function for the real update function
 */
function selection_update() {
    _selection_update(current_cc, $("#Years").val(), $("#ProductCategory").val(), $("#Dimension").val());
}

/**
 *
 * @param cc
 * @param year
 * @param category
 * @param dimension
 * @private
 *
 * First disables all inputs while execution to avoid conflicts
 * Loads the required data from jsons in dependencies of country, year and categories
 * Switch the current selection
 * Update year and categories dropdowns
 * Enables Inputs
 * send request to redraw charts
 */
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
/**
 * Disables the input drop-downs and field for countries, years, categories and
 * trade dimension
 */
function disable_inputs() {
    $("#Country").prop('disabled', true);
    $("#Years").prop('disabled', true);
    $("#ProductCategory").prop('disabled', true);
    $("#Dimension").prop('disabled', true);
}

/**
 * Enables the input drop-downs and field for countries, years, categories and
 * trade dimension
 */
function enable_inputs() {
    $("#Country").prop('disabled', false);
    $("#Years").prop('disabled', false);
    $("#ProductCategory").prop('disabled', false);
    $("#Dimension").prop('disabled', false);
}

/**
 *
 * @param cc
 */
function country_selected(cc) {
    var last_index = countries[cc]["years"][default_category].length - 1;
    var latest_year = countries[cc]["years"][default_category][last_index];
    $("#Dimension").val(default_dimension);
    _selection_update(cc, latest_year, default_category, default_dimension);
}

/**
 * Initial the country selection with auto-complete functionality
 * For more information see autocomplete.js
 */
function init_autocomplete() {
    var country_list = [];

    $.each(countries, function(key, value) {
        if(Object.keys(value["years"]).length > 0) {
            country_list.push(value["full_name"]);
        }
    });

    autocomplete(document.getElementById("Country"), country_list, function(selection) {
        var cc = country_to_cc[selection];
        country_selected(cc);
    });
}
/**
 * Initialize the years for initial and change selection state of the page
 * Shown the available years in a drop down menu
 */
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

/**
 * Initialize the categories for initial and change selection state of the page
 * Shown the available economy categories in a drop down menu
 */
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

/**
 *
 * @param cb -> Function to execute at the end of this function
 * LoadBaseData loads for the initial status countries and the categories for selection
 * With alert when it's fail
 * Safe in global variables
 *
 */

function loadBaseData(cb) {
    $.when( $.getJSON( "/vis_data/countries.json" ), $.getJSON( "/vis_data/categories.json" ) ).done(function( _countries, _categories ) {
        if(_countries[2]["status"] !== 200 || _categories[2]["status"] !== 200) {
            alert("Failed to load base data!");
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

/**
 * init Function to initialize Data from Jsons ressources
 * Define JQuery for change of the dropdown selection for years,categories and trade dimension
 * triggered status initialized
 * hides te LoadingOverlay
 */
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
        $( document ).trigger("initialized");
    });
}

/**
 * JQuery, for detecting if the page ready for manipulation
 * When the Page is ready call the init() function
 */
$( document ).ready(function() {
    init();
});