
;(function(jQuery) {
var tooltipFormatter = function() {
    var tip = '<span style="font-size:12px;font-weight:bold;text-align:center">' + Highcharts.dateFormat('%b %d, %Y', this.x) + '</span>';
    jQuery.each(this.points, function() { if (this.series.type == "line") { tip += '<br/>' + this.y + ' : <span style="color:'+this.color+'">' + this.series.name + '</span>'; } });
    return tip;
};

var ChartController = {
    area_threshold: -999.0,
    callbacks: { },
    chart: null,
    chart_anchor: "#csftool-display-chart",
    chart_labels: { },
    chart_type: null,
    chart_config: { chart:{type:"area"}, plotOptions:{series:{states:{hover:{enabled:true, halo:false}}}},
        credits: { text:"Powered by NRCC", href:"http://www.nrcc.cornell.edu/", color:"#000000" },
        title: { text: 'Grape Hardiness @ T50' },
        subtitle: { text: 'location address', style:{"font-size":"14px", color:"#000000"} },
        xAxis: { type:'datetime', crosshair:{ width:1, color:"#ff0000", snap:true, zIndex:10 }, labels:{ style:{color:"#000000"} },
                 dateTimeLabelFormats:{ millisecond:'%H:%M:%S.%L', second:'%H:%M:%S', minute:'%H:%M', hour:'%H:%M', day:'%d %b', week:'%d %b', month:'%b<br/>%Y', year:'%Y' },
                },
        yAxis: { title:{ text:'Temperature', style:{"font-size":"14px", color:"#000000"}}, gridZIndex:4, labels:{style:{color:"#000000"}},
                 },
        tooltip: { useHtml:true, shared:true, borderColor:"#000000", borderWidth:2, borderRadius:8, shadow:false, backgroundColor:"#ffffff",
                   style:{width:165,}, xDateFormat:"%b %d, %Y", positioner:function(){return {x:80, y:60}}, formatter:tooltipFormatter },
        legend: { floating:true, backgroundColor:"#ffffff", borderRadius:5, borderWidth:1, align:'left', verticalAlign:'top', x:70, y:50, width:165, zIndex:20 },
        series: [ ],
    },

    components: {
        "hardarea" : { name: 'T50 Damage Potential', type:"area", zIndex:2, lineWidth:0, color:"#ffb3b3", marker: { enabled:false, states:{hover:{enabled:false}} } },
        "hardfcast" : { name: "Hardiness Forecast", type:"line", zIndex:12, lineWidth:2, dashStyle:'Dot', color:"#00cc00", marker: { enabled:true, fillColor:"#00cc00", lineWidth:1, lineColor:"#00cc00", radius:3, symbol:"circle" } },
        "hardtemp" : { name: "Hardiness Temp", type:"line", zIndex:11, lineWidth:2, color:"#00cc00", marker: { enabled:true, fillColor:"#00cc00", lineWidth:1, lineColor:"#00cc00", radius:3, symbol:"circle" } },
        "mintarea" : { name: 'No Damage Potential', type:"area", zIndex:3, lineWidth:0, color:"#ffffff", fillOpacity:1.0, showInLegend:false, marker: { enabled:false, states:{hover:{enabled:false}} } },
        "mintemp" : { name: "Min Temperature", type:"line", zIndex:13, lineWidth:2, color:"#0000ff", marker:{enabled:false,} },
        "minfcast" : { name: "Min Temp Forecast", type:"line", zIndex:14, lineWidth:2, dashStyle:'Dot', color:"#0000ff", marker: { enabled:true, fillColor:"#0000ff", lineWidth:1, lineColor:"#0000ff", radius:3, symbol:"circle" } },
    },

    data: { },
    default_chart: null,
    display_anchor: null,
    dom: '<div id="csftool-display-chart"></div>',
    drawn: [ ],
    event_types: [ "drawing_complete", "series_drawn"],
    initialized: false,
    location: null,
    required: ["hardtemp","mintemp"],
    season: null,
    tool: null,
    variety: null,
    varieties: null,
    view: null,

    // FUNCTIONS
    highchartsIsAvailable: function() { return (typeof Highcharts !== "undefined"); },

    addSeries: function(data_type, data) {
        if (data && data.length > 1) {
            if (this.chart == null || typeof this.chart === 'undefined') { this.newChart(); }
            var series = jQuery.extend(true, { id:data_type, data:data}, this.components[data_type]);
            if (data_type == "hardarea" || data_type == "mintarea") { series["threshold"] = this.area_threshold; }
            this.validChart();
            if (this.drawn.indexOf(data_type) > -1) { this.remove(data_type); }
            this.chart.addSeries(series, true);
            if (this.drawn.indexOf(data_type) < 0) { this.drawn.push(data_type); }
            this.execCallback("series_drawn", data_type);
        }
        this.complete();
    },

    allDrawn: function() {
        var all_drawn = true; var i; var self = this;
        jQuery.each(this.required, function(i, data_type) { if (self.drawn.indexOf(data_type) < 0) { all_drawn = false; } } );
        return all_drawn;
    },

    bind: function(event_type, callback) { if (this.event_types.indexOf(event_type) > 0) { this.callbacks[event_type] = callback; } },
    clear: function() { while( this.chart.series.length > 0 ) { this.chart.series[0].remove(false); }; this.drawn = [ ]; },
    chartHeight: function(height) { this.chart_config.chart["height"] = height; },
    chartLabel: function(key, label) { this.chart_labels[key] = label; },
    chartLabels: function(labels) { this.chart_labels = jQuery.extend(this.chart_labels , labels); },
    chartType: function(chart_type) { this.chart_type = chart_type; },
    chartWidth: function(width) { this.chart_config.chart["width"] = width; },
    complete: function(reset) { if (this.allDrawn()) { this.execCallback("drawing_complete"); } },

    dataExtremes: function(data_array) {
        var i, value;
        var max = -999.; var min = 999.;
        for (i = 0; i < data_array.length; i++) {
            value = data_array[i][1];
            if (value > max) { max = value; }
            if (value < min) { min = value; }
        }
        return [min, max];
    },

    draw: function() {
        this.tool.logObjectAttrs(this.view);
        var mint = this.tool.fullview("mint", this.view);
        var extremes = this.dataExtremes(mint);
        var min_mint = extremes[0];
        var hardtemp = this.tool.fullview("hardtemp", this.view);
        extremes = this.dataExtremes(hardtemp);
        if (min_mint < extremes[0]) {
            this.area_threshold = min_mint - 5.0;
            this.addSeries("mintarea", mint);
            this.addSeries("hardarea", hardtemp);
        }
        this.addSeries("hardtemp", this.tool.observed("hardtemp", this.view));
        this.addSeries("hardfcast", this.tool.forecast("hardtemp", this.view));
        this.addSeries("mintemp", this.tool.observed("mint", this.view));
        this.addSeries("minfcast", this.tool.forecast("mint", this.view));
    },

    drawChartLabel: function() {
        var label = this.season + " " + this.chart_labels[this.chart_type];
        this.chart.renderer.text(label, 325, 85).css({ color:"#000000", fontSize:"16px"}).add();
    },

    drawErrorLabel: function(season) {
        var label = season + " Season is not avalaible";
        this.chart.renderer.text(label, 200, 85).css({ color: "#ff0000", fontSize: "20px"}).add();
    },

    execCallback: function(event_type, info) {
        var callback = this.callbacks[event_type];
        if (callback) {
            if (info) { callback(event_type, [info,jQuery.extend([],this.drawn)]);
            } else { callback(event_type, jQuery.extend([],this.drawn)); }
        }
    },

    init: function(dom_element) {
        this.display_anchor = "#" + dom_element.id;
        jQuery(this.display_anchor).append(this.dom);
        Highcharts.setOptions({ global: { useUTC: false } });
        this.initialized = true;
        if (this.chart_type == null) { this.chart_type = this.default_chart; }
    },

    locationChange: function(loc_obj) {
        if (this.location == null || loc_obj.address != this.location) { this.location = loc_obj.address; }
        if ("variety" in loc_obj) { this.varietyChange(loc_obj.variety) }
    },

    newChart: function() {
        if (this.chart != null) { this.chart.destroy(); this.chart = null; }
        var config = jQuery.extend(true, { }, this.chart_config);
        config.series = [ ];
        config.title.text = this.title();
        config.subtitle.text = this.subtitle();
        jQuery(this.chart_anchor).highcharts("Chart", config);
        this.chart = jQuery(this.chart_anchor).highcharts();
        if (arguments.length == 0) { this.drawChartLabel();
        } else { this.drawErrorLabel(arguments[0]); }
        this.drawn = [ ];
    },

    redraw: function() { this.newChart(); this.draw(); },
    refresh: function() { this.clear(); this.draw(); },
    remove: function(series_key) {
        if (this.chart != null) {
            if (typeof series_key !== 'undefined') {
                var i;
                var name = this.components[series_key].name;
                var num_series = this.chart.series.length;
                for(i = 0; i < num_series; i++) { if (this.chart.series[i].name == name) { this.chart.series[i].remove(); break; } }
            } else { this.chart.destroy(); this.chart = null; }
        }
    },

    resetExtremes: function() { this.yaxis_max = -999.0; this.yaxis_min = 999.0; },

    setOption: function(key, value) {
        switch(key) {
            case "chart":
            case "chart_type": this.chartType(value); break;
            case "default": this.default_chart = value; break;
            case "height": this.chartHeight(value); break;
            case "labels": this.chartLabels(value); break;
            case "location": this.locationChange(value); break;
            case "season": this.season = value; break;
            case "variety": this.varietyChange(value); break;
            case "varieties": this.varieties = value; break;
            case "view": this.setView(value); break;
            case "width": this.chartWidth(value); break;
        }
    },

    setOptions: function(options) {
        jQuery.each(options, function (i) {
            var option = options[i];
            for (var key in option) { ChartController.setOption(key, option[key]); }
        });
    },

    setView: function(view_obj) { this.view = jQuery.extend({}, view_obj); },
    subtitle: function() { return "@ " + this.location; },
    title: function() { return this.varieties[this.variety] + " T50 Hardiness Temperature"; },
    validChart: function() { if (this.chart === null) { this.newChart(); } },
    varietyChange: function(variety) { if (this.variety == null) { this.variety = variety; } else if (variety != this.variety) { this.variety = variety; } },
}

var jQueryDisplayProxy = function() {
    if (arguments.length == 1) {
        switch(arguments[0]) {
            case "chart": // return currently displayed chart type
            case "chart_type":
                return ChartController.chart_type;
                break;
            case "chart_anchor": return ChartController.chart_anchor; break;
            case "display_anchor": return ChartController.display_anchor; break;
            case "draw": ChartController.draw(); break;
            case "drawn": return ChartController.drawn; break;
            case "location": return ChartController.location; break;
            case "newChart": ChartController.newChart(); break;
            case "redraw": ChartController.redraw(); break;
            case "refresh": ChartController.refresh(); break;
            case "season": return ChartController.season; break;
            case "start_date": return ChartController.start_date; break;
            case "variety": return ChartController.variety; break;
            case "view": return ChartController.view; break;
        } // end of single argument switch

    } else if (arguments.length == 2) {
        var arg_0 = arguments[0];
        var arg_1 = arguments[1];
        switch(arg_0) {
            case "options": ChartController.setOptions(arg_1); break;
            case "show_error": ChartController.newChart(arg_1); break;
            default: ChartController.setOption(arg_0, arg_1); break;
        } // end of 2 argument switch

    } else if (arguments[0] == "option") { ChartController.setOption(arguments[1], arguments[2]);
    } else if (arguments[0] == "bind") { ChartController.bind(arguments[1], arguments[2]); }
    return undefined;
}

jQuery.fn.GrapeHardinessChart = function(tool, options) {
    var dom_element = this.get(0);
    ChartController.tool = tool;
    if (jQuery.type(options) !== 'undefined') { jQuery.each(options, function(i,option) { jQueryDisplayProxy.apply(jQueryDisplayProxy, option); }); }
    ChartController.init(dom_element);
    return [ ChartController, jQueryDisplayProxy ];
}

})(jQuery);

