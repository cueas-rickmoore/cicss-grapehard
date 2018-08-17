;jQuery(document).ready( function () {
    GRAPEHARD.wait_widget.widget_anchor = '#csftool-display';
    GRAPEHARD.wait_widget.createDialog({ center_on: "#csftool-display", });
    GRAPEHARD.wait_widget.bind("allItemsAvailable", function(ev, items) {
        GRAPEHARD.display("redraw");
        GRAPEHARD.wait_widget.stop(true);
    });

    GRAPEHARD.addListener("load.onComplete", function(manager) { if (typeof GRAPEHARD.display !== 'undefined') { GRAPEHARD.display("redraw"); } });

    var options = [
          [ 'chart', 'default', GRAPEHARD.default_chart ],
          [ 'chart', 'labels', GRAPEHARD.chart_labels ],
          [ 'chart', 'types', GRAPEHARD.chart_types ],
          [ 'date', 'select', GRAPEHARD.locations.doi ],
          [ 'date', 'button', GRAPEHARD.csf_common_url+"/icons/calendar-24x24.png"],
          [ 'date', 'range', GRAPEHARD.dates.season_start, GRAPEHARD.dates.season_end ],
          [ 'date', 'years', GRAPEHARD.min_year, GRAPEHARD.max_year ],
          [ 'location', 'default',  GRAPEHARD.locations.state ],
          [ 'varieties', GRAPEHARD.varieties ],
          [ 'variety', GRAPEHARD.locations.variety ],
          ];
    GRAPEHARD.ui = jQuery(GRAPEHARD.ui_anchor).GrapeHardinessUserInterface(options);

    options = [ [ 'chart_type', GRAPEHARD.ui.option("chart") ],
                [ 'default', "trend" ],
                [ 'height', 450 ],
                [ 'labels', GRAPEHARD.chart_labels ],
                [ 'location', GRAPEHARD.locations.state ],
                [ 'season', GRAPEHARD.dates.season_spread ],
                [ 'varieties', GRAPEHARD.varieties ],
                [ 'view', GRAPEHARD.dates.view ],
                [ 'width', 700 ],
              ];
    var result = jQuery(GRAPEHARD.display_anchor).GrapeHardinessChart(GRAPEHARD, options);
    GRAPEHARD.chart_controller = result[0];
    GRAPEHARD.display = result[1];
    GRAPEHARD.display("bind", "drawing_complete", function(ev, drawn) { GRAPEHARD.wait_widget.stop(true); });
    GRAPEHARD.displayReady();
    GRAPEHARD.display("newChart");
    if (GRAPEHARD.wait_widget.isavailable("hardtemp") && GRAPEHARD.wait_widget.isavailable("tempexts")) { GRAPEHARD.display("draw"); }

    GRAPEHARD.data.addListener("hardinessChanged", function(ev) { GRAPEHARD.dataChanged('hardtemp'); });
    GRAPEHARD.data.addListener("tempextsChanged", function(ev) { GRAPEHARD.dataChanged('tempexts'); });
    GRAPEHARD.data.addListener("allDataRequested", function(ev) { GRAPEHARD.display("remove"); GRAPEHARD.wait_widget.start(['hardtemp','tempexts']); });
    GRAPEHARD.dates.addListener("seasonChanged", function(ev, year) { GRAPEHARD.uploadAllData(); });
    GRAPEHARD.locations.addListener("varietyChanged", function(ev, variety) { GRAPEHARD.display("variety", variety); GRAPEHARD.uploadSeasonData(); });
    GRAPEHARD.locations.addListener("locationChanged", function(ev, loc_obj, changes) { GRAPEHARD.display("remove"); GRAPEHARD.display("location", loc_obj); GRAPEHARD.uploadSeasonData(loc_obj); });

    GRAPEHARD.dates.addListener("viewChanged", function(ev, view_obj) {
        GRAPEHARD.logObjectAttrs(view_obj);
        if (GRAPEHARD.display('chart_type') == "trend") {
            GRAPEHARD.display('view', view_obj);
            GRAPEHARD.display('draw');
        }
    });

    var ui = GRAPEHARD.ui;

    ui.option("bind", "chartChangeRequest", function(ev, chart_type) {
        if (chart_type == "season") { GRAPEHARD.display("view", GRAPEHARD.dates.season_view);
        } else if (chart_type == "trend") { GRAPEHARD.display("view", GRAPEHARD.dates.view); }
        GRAPEHARD.display("chart_type", chart_type);
        GRAPEHARD.display("redraw");
    });

    ui.option("bind", "dateChanged", function(ev, doi) { GRAPEHARD.dateChanged(doi); });
    ui.option("bind", "locationChanged", function(ev, loc_obj) { if (!(jQuery.type(loc_obj.address) === 'undefined')) { GRAPEHARD.locations.update(loc_obj); } });
    ui.option("bind", "locationChangeRequest", function(ev, loc_obj) { GRAPEHARD.map_dialog("open", loc_obj.id); });
    ui.option("bind", "varietyChanged", function(ev, variety) { GRAPEHARD.locations.variety = variety; });

    if (typeof NO_MAP_DAILOG === 'undefined') {
        var options = { width:600, height:500, google:google, default:GRAPEHARD.locations.state };
        jQuery("#csftool-input").append(GRAPEHARD.map_dialog_container);
        jQuery(GRAPEHARD.map_dialog_anchor).CsfToolLocationDialog(options);
        var map_dialog = jQuery(GRAPEHARD.map_dialog_anchor).CsfToolLocationDialog();
        GRAPEHARD.map_dialog = map_dialog;
        map_dialog("locations", GRAPEHARD.locations.locations);

        map_dialog("bind", "close", function(ev, context) { 
            if (context.selected_location != context.initial_location) {
                var loc_obj = context.selected_location;
                GRAPEHARD.ui.option("location", loc_obj);
            }
        });
    }
});
