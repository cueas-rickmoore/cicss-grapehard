GRAPEHARD = {
    _listeners_: { },
    available: [ ],
    button_labels: {{ button_labels }},
    chart_labels: {{ chart_labels }},
    chart_types: {{ chart_types }},
    csf_common_url: "{{ csftool_url }}",
    data: null,
    dates: null,
    default_chart: "{{ default_chart }}",
    display: null,
    display_anchor: "#csftool-display",
    location: null,
    map_dialog_anchor: "#grapehard-location-anchor",
    map_dialog_container: '<div id="grapehard-location-anchor"> </div>',
    max_year: {{ max_year }},
    min_year: {{ min_year }},
    season: "{{ season_description }}",
    server_url: "{{ server_url }}",
    supported_listeners: ["allDataAvailable", "onDataRequest", "onStopWaitWidget"],
    tool_url: "{{ tool_url }}",
    toolname: "{{ toolname }}",
    ui: null,
    ui_anchor: "#csftool-input",
    varieties: {{ varieties_js }},
    waiting_for: [],
    wait_widget: null,

    addCorsHeader: function(xhr) {
        xhr.setRequestHeader('Content-Type', 'text/plain');
        xhr.setRequestHeader('Access-Control-Request-Method', 'GET');
        xhr.setRequestHeader('Access-Control-Request-Headers', 'X-Requested-With');
        xhr.withCredentials = true;
    },

    addListener: function(event_type, function_to_call) {
        if (event_type.substring(0,6) != "load.") {
            var index = this.supported_listeners.indexOf(event_type);
            if (index >= 0) { this._listeners_[event_type] = function_to_call; }
        } else{ this.wait_widget.addListener(event_type.split('.')[1], function_to_call); }
    },

    adjustTimeZone: function(date_value) { return new Date(date_value.toISOString().split('T')[0]+'T12:00:00-04:30'); },
    allDataAvailable: function() { if (this.available.length == 0) { return false } else { return (jQuery(this.available).not(this.waiting_for).length === 0) && (jQuery(this.waiting_for).not(this.available).length === 0); } },

    dataChanged: function(data_type) {
        if (this.available.indexOf(data_type) < 0) { 
            this.available.push(data_type);
            if (this.wait_widget && this.wait_widget.waiting()) { this.wait_widget.available(data_type); }
        }
        if (this.allDataAvailable() && "allDataAvailable" in this._listeners_) { this._listeners_.allDataAvailable("allDataAvailable", jQuery.extend([],this.available)); }
    },

    dateChanged: function(new_date) {
        var doi = this.dateToDateObj(new_date);
        this.locations.doi = doi;
        this.dates.doi = doi;
    },

    dateToDateObj: function(date_value) {
        if (jQuery.type(date_value) === 'string') { return new Date(date_value+'T12:00:00-04:30'); 
        } else if (jQuery.isArray(date_value)) {
            if (date_value.length == 3) { return this.adjustTimeZone(new Date(date_value[0], date_value[1]-1, date_value[2]));
            } else if (date_value.length == 2) { return this.dayToDateObj(date_value); }
        } else { return this.adjustTimeZone(date_value); }
    },

    displayReady: function() {
        if (this.data.hardtemp.length > 0) { this.display("addSeries", "hardiness");}
        if (this.data.mint.length > 0) { this.display("addSeries", "mint");  }
    },

    forecast: function(data_type, view) {
        var _view; if (typeof view !== 'undefined') { _view = view; } else { _view = this.dates.view; }
        var fcast_view = this.dates.forecastView(_view);
        if (fcast_view) { return this.genDataPairs(data_type, fcast_view.start, fcast_view.end); } else { return; }
    },

    fullview: function(data_type, view) {
        var _view; if (typeof view !== 'undefined') { _view = view; } else { _view = this.dates.view; }
        if (jQuery.type(data_type) === 'string') { return this.genDataPairs(data_type, _view.start, _view.end);
        } else if (jQuery.isArray(data_type)) { return this.genDataRange(data_type[0], data_type[1], _view.start, -view.end);
        } else { return; }
    },

    genDataPairs: function(data_type, start, end) {
        var end_index = this.dates.indexOf(end) + 1;
        var start_index = this.dates.indexOf(start);
        var slice = this.data.slice(data_type, start_index, end_index);
        var days = this.dates.slice(start_index, end_index);
        var pairs = [ ];
        for (var i=0; i < slice.length; i++) { pairs.push([ days[i], slice[i] ]); }
        return pairs;
    },

    isavailable: function(data_type) { return (this.available.indexOf(data_type) > -1); },
    load_is_complete: function() { return this.wait_widget.allItemsAvailable(); },

    logObjectAttrs: function(obj) { jQuery.each(obj, function(key, value) { console.log("    ATTRIBUTE " + key + " = " + value); }); },
    logObjectHtml: function(container) { if (jQuery.type(container) === 'string') { var element = document.getElementById(container); } },

    observed: function(data_type, view) {
        var _view = this.dates.observedView(view);
        if (jQuery.type(data_type) === 'string') { return this.genDataPairs(data_type, _view.start, _view.end);
        } else if (jQuery.isArray(data_type)) { return this.genDataRange(data_type[0], data_type[1], _view.start, -view.end);
        } else { return; }
    },

    startWaitWidget: function() { if (arguments.length == 1) { this.wait_widget.start(arguments[0]); } else if (arguments.length == 2) { this.wait_widget.start(arguments[0], arguments[1]); } },
    stopWaitWidget: function() { this.wait_widget.stop(); },

    uploadAllData: function(requested_loc) {
        var loc_obj = requested_loc;
        if (jQuery.type(loc_obj) === 'undefined') { loc_obj = this.locations.state; 
        } else { this.locations.update(loc_obj, false); }
        this.available = [ ];
        this.waiting_for = ['days', 'hardtemp', 'tempexts'];
        if ("onDataRequest" in this._listeners_) { this._listeners_.allDataAvailable("onDataRequest",  jQuery.extend([],this.waiting_for)); }
        this.dates.uploadDaysInSeason();
        this.data.uploadHardinessData(loc_obj);
        this.data.uploadTempextData(loc_obj);
    },

    uploadSeasonData: function(loc_obj) {
        var loc_obj = loc_obj;
        if (jQuery.type(loc_obj) === 'undefined') { loc_obj = this.locations.state; }
        this.available = [ ];
        this.waiting_for = ['hardtemp', 'tempexts'];
        if ("onDataRequest" in this._listeners_) { this._listeners_.allDataAvailable("onDataRequest",  jQuery.extend([],this.waiting_for)); }
        this.data.uploadHardinessData(loc_obj);
        this.data.uploadTempextData(loc_obj);
    },

    varietyName: function(key) { return this.varieties[key]; },
    waitFor: function(data_type) { this.wait_widget.waitFor(data_type); },
}

function ToolDataManager(tool) {
    var _data_, _listeners_;
    this._data_ = { "hardtemp":[], "mint":[], }
    this._listeners_ = { }

    var  error_callbacks, tool, upload_callbacks;
    this.error_callbacks = { tempexts: null, hardtemp: null };
    this.tool = tool;
    this.upload_callbacks = { tempexts: null, hardtemp: null };
 
    Object.defineProperty(this, "available_types", {
        configurable:false, enumerable:true, 
        get:function() { var available = [ ];
            if (this._data_.hardtemp.length > 0) { available.push("hardtemp"); }
            if (this._data_.mint.length > 0) { available.push("tempexts"); }
            return available;
        },
    });
    Object.defineProperty(this, "data_arrays", { configurable:false, enumerable:false, writable:false, value: ["hardtemp", "mint"] });
    Object.defineProperty(this, "data_types", { configurable:false, enumerable:false, writable:false, value: ["hardtemp", "mint"] });
    Object.defineProperty(this, "hardtemp", { configurable:false, enumerable:true, get:function() { return this._data_.hardtemp; } });
    Object.defineProperty(this, "mint", { configurable:false, enumerable:true, get:function() { return this._data_.mint } });
    Object.defineProperty(this, "supported_listeners", { configurable:false, enumerable:false, writable:false, value: ["allDataRequested", "hardtempChanged", "tempextsChanged"] });
}

ToolDataManager.prototype.addListener = function(event_type, function_to_call) {
    var index = this.supported_listeners.indexOf(event_type);
    if (index >= 0) { this._listeners_[event_type] = function_to_call; }
}

ToolDataManager.prototype.dataAt = function(data_type, index) { return this._data_[data_type][index]; }
ToolDataManager.prototype.dataLength = function(data_type) { return this._data_[data_type].length; }

ToolDataManager.prototype.slice = function(data_type, start_index, end_index) {
    if (start_index > 0) {
        if (end_index > 0) {
            return this._data_[data_type].slice(start_index, end_index);
        } else { return this._data_[data_type].slice(start_index); }
    } else {
        if (end_index > 0) { 
           return this._data_[data_type].slice(0, end_index);
        } else { return; }  
    }
}

ToolDataManager.prototype.updateHardtemp = function(data) { this._data_.hardtemp = data; if ("hardtempChanged" in this._listeners_) { this._listeners_.hardtempChanged("hardtempChanged"); } }
ToolDataManager.prototype.updateTempexts = function(data) { this._data_.mint = data; if ("tempextsChanged" in this._listeners_) { this._listeners_.tempextsChanged("tempextsChanged"); } }

ToolDataManager.prototype.uploadAllData = function (loc_obj) {
    if ("allDataRequested" in this._listeners_) { this._listeners_.allDataRequested("allDataRequested"); }
    this.uploadHardinessData(loc_obj); 
    this.uploadTempextData(loc_obj);
}

ToolDataManager.prototype.uploadHardinessData = function (loc_obj) {
    var url = this.tool.tool_url + '/hardtemp';
    var query = {location:{key:loc_obj.id, address:loc_obj.address, coords:[loc_obj.lat,loc_obj.lng]}, variety:loc_obj.variety, season:this.tool.dates.season};
    query = JSON.stringify(query);
    var options = { url:url, type:'post', dataType:'json', crossDomain:true, data:query,
                    error:this.error_callbacks.hardtemp, success:this.upload_callbacks.hardtemp,
                    beforeSend: function(xhr) { GRAPEHARD.addCorsHeader(xhr); GRAPEHARD.waitFor("hardtemp"); },
    }
    jQuery.ajax(options);
}

ToolDataManager.prototype.uploadTempextData = function(loc_obj) {
    var url = this.tool.tool_url + '/tempexts';
    var query = {location:{key:loc_obj.id, address:loc_obj.address, coords:[loc_obj.lat,loc_obj.lng]}, variety:loc_obj.variety, season:this.tool.dates.season};
    query = JSON.stringify(query);
    var options = { url:url, type:'post', dataType:'json', crossDomain:true, data:query,
                    error: this.error_callbacks.tempexts, success: this.upload_callbacks.tempexts,
                    beforeSend: function(xhr) { GRAPEHARD.addCorsHeader(xhr); GRAPEHARD.waitFor("tempexts"); }
    }
    jQuery.ajax(options);
}

function ToolDatesManager(tool) {
    var _dates_, _days_, _listeners_;
    this._dates_ = { days_in_view:{{ days_in_view }}, doi: null, fcast_start:null, fcast_end:null, last_obs:null, last_valid:null,
                     season:null, season_end:null, season_spread:null, season_start:null, view_end:null, view_start:null };
    this._days_ = [ ];
    this._listeners_ = { };

    var default_doi, error_callback, season_end_day, season_is_clipped, season_start_day, tool, upload_callback;
    this.default_doi = {{ default_doi }};
    this.error_callback = null;
    this.ms_per_day = 24*3600*1000;
    this.season_end_day = null;
    this.season_is_clipped = false;
    this.season_start_day = null;
    this.tool = tool;
    this.upload_callback = null;

    Object.defineProperty(this, "days", {
        configurable:false, enumerable:true,
        get:function() { return this._days_; },
        set:function(days_array) {
                var date_mgr = this
                this._days_ = days_array.map(function(day) { return date_mgr.dateToTime(day); });
                if ("daysChanged" in this._listeners_) { this._listeners_.daysChanged("daysChanged", this._days_); }
            }
    });

    Object.defineProperty(this, "days_in_season", { configurable:false, enumerable:false, get:function() { return this._days_.length; } });

    Object.defineProperty(this, "days_in_view", {
        configurable:false, enumerable:false,
        get:function() { return this._days_.days_in_view; },
        set:function(num_days) { this._days_.days_in_view = Number(num_days); this._updateView_(); },
    });

    Object.defineProperty(this, "doi", {
        configurable:false, enumerable:false,
        get:function() { var doi = this._dates_.doi; if (doi) { return doi; } else { return this.default_doi; } },
        set:function(new_date) {
            var doi = this.dateToDateObj(new_date);
            if (doi != this._dates_.doi) { this._dates_.doi = doi; this._updateView_(); }
        }
    });

    Object.defineProperty(this, "fcast_end", {
        configurable:false, enumerable:true,
        get:function() { if (this._dates_.fcast_end instanceof Date) { return this._dates_.fcast_end; } else { return null } },
        set:function(new_date) {
            if (jQuery.type(new_date) === 'string' || new_date instanceof Date) {
                var fcast_end = this.dateToDateObj(new_date);
                if (fcast_end <= this.season_end) { this._dates_.fcast_end = fcast_end; } else { this._dates_.fcast_end = null; }
            } else { this._dates_.fcast_end = null; }
        }
    });

    Object.defineProperty(this, "fcast_start", {
        configurable:false, enumerable:true,
        get:function() { if (this._dates_.fcast_start instanceof Date) { return this._dates_.fcast_start; } else { return null } },
        set:function(new_date) {
            if (jQuery.type(new_date) === 'string' || new_date instanceof Date) {
                var fcast_start = this.dateToDateObj(new_date);
                if (fcast_start <= this.season_end) { this._dates_["fcast_start"] = fcast_start; } else { this._dates_["fcast_start"] = null; }
            } else { this._dates_.fcast_start = null; }
        }
    });

    Object.defineProperty(this, "last_obs", {
        configurable:false, enumerable:true,
        get:function() { return this._dates_["last_obs"]; },
        set:function(new_date) {
            var last_obs = this.dateToDateObj(new_date);
            if (last_obs < this.season_end) { this._dates_["last_obs"] = last_obs; } else { this._dates_["last_obs"] = this.season_end; }
        }
    });

    Object.defineProperty(this, "last_valid", {
        configurable:false, enumerable:true,
        get:function() {
            if (this._dates_.last_valid instanceof Date) { return this._dates_.last_valid; }
            if (this._dates_.fcast_end instanceof Date) { return this._dates_.fcast_end; }
            if (this._dates_.last_obs instanceof Date) { return this._dates_.last_obs; }
            return this.season_end;
        },
        set:function(new_date) {
            var last_valid = this.dateToDateObj(new_date);
            if (last_valid < this.season_end) { this._dates_.last_valid = last_valid;
            } else { this._dates_.last_valid = this.season_end; }
        },
    });

    Object.defineProperty(this, "season", { 
        configurable:false, enumerable:false,
        get:function() { return this._dates_["season"]; },
        set:function(year) {
            var prev_year = this._dates_['season'];
            var new_year = Number(year);
            if (new_year != prev_year) {
                this._dates_.season = new_year;
                this._dates_.season_end = this.dayToDateObj(this.season_end_day);
                this._dates_.season_start = this.dayToDateObj(this.season_start_day);
                this._dates_.season_spread = (new_year-1).toString() + "-" + new_year.toString();
                if (prev_year != null && "seasonChanged" in this._listeners_) { this._listeners_.seasonChanged("seasonChanged", new_year); }
            }
        }
    });

    Object.defineProperty(this, "season_end", { configurable:false, enumerable:false, get:function() { return this._dates_.season_end; } });
    Object.defineProperty(this, "season_spread", { configurable:false, enumerable:false, get:function() { return this._dates_.season_spread; } });
    Object.defineProperty(this, "season_start", { configurable:false, enumerable:false, get:function() { return this._dates_.season_start; } });
    Object.defineProperty(this, "season_view", { configurable:false, enumerable:false, get:function() { return this.seasonView(); } });

    Object.defineProperty(this, "supported_listeners", { configurable:false, enumerable:false, writable:false,
        value: [ "datesChanged", "daysChanged", "seasonChanged", "viewChanged"]
    });

    Object.defineProperty(this, "view", { configurable:false, enumerable:false, get:function() { return { doi:this._dates_.doi, end:this._dates_.view_end, start:this._dates_.view_start } } });
    Object.defineProperty(this, "view_end", { configurable:false, enumerable:false, get:function() { return this._dates_.view_end; } });
    Object.defineProperty(this, "view_start", { configurable:false, enumerable:false, get:function() { return this._dates_.view_start; } });
}

ToolDatesManager.prototype.addListener = function(event_type, function_to_call) {
    var index = this.supported_listeners.indexOf(event_type);
    if (index >= 0) { this._listeners_[event_type] = function_to_call; }
}

ToolDatesManager.prototype.adjustTimeZone = function(date_value) {
    return new Date(date_value.toISOString().split('T')[0]+'T12:00:00-04:30'); }

ToolDatesManager.prototype.dateToDateObj = function(date_value) {
    if (jQuery.type(date_value) === 'string') { return new Date(date_value+'T12:00:00-04:30'); 
    } else if (jQuery.isArray(date_value)) {
        if (date_value.length == 3) { return this.adjustTimeZone(new Date(date_value[0], date_value[1]-1, date_value[2]));
        } else if (date_value.length == 2) { return this.dayToDateObj(date_value); }
    } else { return this.adjustTimeZone(date_value); }
}
ToolDatesManager.prototype.dateToString = function(date_value) { if (jQuery.type(date_value) === 'string') { return date_value } else { return this.dateToDateObj(date_value).toISOString().split("T")[0]; } }
ToolDatesManager.prototype.dateToTime = function(date_value) { if (date_value instanceof Date) { return date_value.getTime(); } else { return new Date(date_value+'T12:00:00-04:30').getTime(); } }
ToolDatesManager.prototype.dayToDateObj = function(day) {
    if (day[0] >= this.season_start_day[0]) { return this.adjustTimeZone(new Date(this.season-1,day[0]-1,day[1]));
    } else { return this.adjustTimeZone(new Date(this.season,day[0]-1,day[1])); }
}

ToolDatesManager.prototype.diffInDays = function(date_1, date_2) { return Math.ceil(Math.abs(date_2.getTime() - date_1.getTime()) / this.ms_per_day); }

ToolDatesManager.prototype.forecastView = function(view) {
    if (this._dates_.fcast_start) { 
        var fcast_start = this._dates_.fcast_start;
        var _view = view; if (typeof view === 'undefined') { _view = this.view; }
        if (fcast_start >= _view.start && fcast_start <= _view.end) {
            if (this._dates_.fcast_end <= _view.end) { 
                return { doi:_view.doi, end:this._dates_.fcast_end, start:fcast_start };
            } else { return { doi:_view.doi, end:_view.end, start:fcast_start }; }
        }
    }
    return;
}

ToolDatesManager.prototype.futureDate = function(from_date, days_in_future) {
    if (typeof days_in_future !== 'undefined') {
        return new Date(from_date.getTime() + days_in_future*this.ms_per_day);
    } else { return new Date(from_date.getTime() + this.ms_per_day); }
}

ToolDatesManager.prototype.indexOf = function(date_) {
    if (date_ instanceof Date) { return this._days_.indexOf(date_.getTime());
    } else if (jQuery.type(date_) === 'string') {
        var the_date = this._dates_[date_];
        if (the_date !== null) { return this._days_.indexOf(the_date.getTime()); }
    } else { return -1; }
}

ToolDatesManager.prototype.init = function(season, season_start_day, season_end_day, default_doi, doi) {
    this.season_start_day = season_start_day;
    this.season_end_day = season_end_day;
    this.season = season;
    if (jQuery.type(default_doi) === 'string') { this.default_doi = this.dateToDateObj(default_doi);
    } else  if (jQuery.isArray(default_doi)) { this.default_doi = this.dayToDateObj(default_doi); }
    if (jQuery.type(doi) === 'string') { this._dates_.doi = this.dateToDateObj(doi);
    } else if (jQuery.isArray(doi)) { this.doi = this.dayToDateObj(doi); }
    this._updateView_();
}

ToolDatesManager.prototype.isValidDate = function(any_date) {
    var month = any_date.getMonth() + 1;
    var day = any_date.getDate();
    if (month >= this.start_day[0] && day >= this.start_day[1]) { return true; }
    if (month <= this.end_day[0] && day <= this.end_day[1]) { return true; }
    return false;
}

ToolDatesManager.prototype.observedView = function(view) {
    var _view = view; if (typeof view === 'undefined') { _view = this.view; }
    if (this._dates_.fcast_start) { 
        var fcast_start = this._dates_.fcast_start;
        if (fcast_start >= _view.start && fcast_start <= _view.end) {
            return { doi:this.doi, end:this.pastDate(fcast_start), start:_view.start };
        }
    }
    return _view;
}

ToolDatesManager.prototype.pastDate = function(from_date, days_in_past) {
    if (typeof days_in_past !== 'undefined') { 
        return new Date( from_date.getTime() - days_in_past*this.ms_per_day);
    } else { return new Date( from_date.getTime() - this.ms_per_day); }
}

ToolDatesManager.prototype.seasonForDate = function(any_date) {
    var year = any_date.getFullyear();
    var start_date = this.adjustTimeZone(new Date(year,start_day[0]-1,start_day[1]));
    if (any_date >= start_date) { return [year, year+1]; } else { return [year-1, year] }
    var end_date = this.adjustTimeZone(new Date(year,end_day[0]-1,end_day[1]));
    if (any_date <= end_date) { return [year-1, year]; } else { return [year, year+1] }
}

ToolDatesManager.prototype.seasonDescription = function(start_year, end_year) {
    return start_year.toString() + "-" + end_year.toString() + " Season";
}

ToolDatesManager.prototype.seasonDescriptionFromDate = function(any_date) {
    var year = any_date.getFullyear();
    // date must be in a valid year 
    if (year > this.tool.max_year || year < this.tool.min_year) { return this.seasonDescription(year-1); }
    // check whether any_date is within valid bounds for a season starting in that year
    var start_date = this.adjustTimeZone(new Date(year,this.season_start_day[0]-1,this.season_start_day[1]));
    if (any_date < start_date) { return this.seasonDescription(year-1); } // any_date is in and earlier season
    var end_date = this.adjustTimeZone(new Date(year+1,this.season_end_day[0]-1,this.season_end_day[1]));
    if (any_date > end_date) { return this.seasonDescription(year); }
    var month = any_date.getMonth() + 1;
    if (month >= this.season_start_day[0]) { return this.seasonDescription(year+1);
    } else { return this.seasonDescription(year); }
}

ToolDatesManager.prototype.seasonView = function() { return { start:this.season_start, end:this.last_valid, doi:this._dates_.doi }; }

ToolDatesManager.prototype.slice = function(start, end) {
    if (jQuery.type(start) == 'number') { return this.sliceByIndex(start, end);
    } else if (start instanceof Date) {
        var end_index = this.indexOf(end);
        var start_index = this.indexOf(start_date);
        return this.sliceByIndex(start_index, end_index);
    }
    return;
}

ToolDatesManager.prototype.sliceByIndex = function(start, end) {
    if (start > 0) { if (end > 0) { return this._days_.slice(start, end); } else { return this._days_.slice(start); }
    } else { if (end > 0) { return this._days_.slice(0, end); } else { return; }  }
}

ToolDatesManager.prototype.update = function(dates_obj) {
    var changed = [];
    if ("fcast_start" in dates_obj) { this.fcast_start = dates_obj["fcast_start"]; changed.push("fcast_start"); } else { this.fcast_start = null; }
    if ("fcast_end" in dates_obj) { this.fcast_end = dates_obj["fcast_end"]; changed.push("fcast_end"); } else { this.fcast_end = null; }
    if ("last_obs" in dates_obj) { this.last_obs = dates_obj["last_obs"]; changed.push("last_obs"); }
    if ("last_valid" in dates_obj) { this.last_valid = dates_obj["last_valid"]; changed.push("last_valid"); }
    if (changed.length > 0) { this._updateView_(); if ("datesChanged" in this._listeners_) { this._listeners_.onUpdate("datesChanged", changed); } }
}

ToolDatesManager.prototype.uploadDaysInSeason = function() {
    var url = this.tool.tool_url + '/daysInSeason';
    var query = JSON.stringify(this.season_view);
    var options = { url:url, type:'post', dataType:'json', crossDomain:true, data:query,
        error: this.error_callback, success: this.upload_callback,
        beforeSend: function(xhr) { GRAPEHARD.addCorsHeader(xhr); GRAPEHARD.waitFor("days"); },
    }
    jQuery.ajax(options);
}

ToolDatesManager.prototype.viewIndexes = function(view) { return { doi: this.indexOf(view.doi), end: this.indexOf(view.end), start: this.indexOf(view.start) }; }

ToolDatesManager.prototype._updateView_ = function() {
    var doi = this._dates_.doi;
    var view_end = this.futureDate(doi, (this._dates_.days_in_view / 2));
    if (this._dates_.last_valid) { // make sure view_end <= last valid date
        if (view_end > this._dates_.last_valid) { view_end = this._dates_.last_valid; }
    } else { // last_valid not set, make sure view_end <= season end date
        if (view_end > this._dates_.season_end) { view_end = this._dates_.season_end; }
    }
    this._dates_.view_end = view_end;
    // set view span from view end date backward
    var view_start = this.pastDate(view_end, this._dates_.days_in_view-1);
    //!TODO : make sure view_start >= season_start
    if (view_start < this._dates_.season_start) { view_start = this._dates_.season_start; }
    this._dates_.view_start = view_start;
    if ("viewChanged" in this._listeners_) { this._listeners_.viewChanged("viewChanged", this.view); }
}

function ToolLocationsManager(tool) {
    var _listeners_, _locations_, _state_;
    this._listeners_ = { };
    this._locations_ = { };
    this._state_ = { address:null, doi:null, id:null, lat:null, lng:null, variety:null };

    var tool;
    this.tool = tool;

    // protected properties
    Object.defineProperty(ToolLocationsManager.prototype, "doi", { configurable:false, enumerable:false,
        get:function() { return this._state_.doi; },
        set:function(new_date) {
            var doi = this.tool.dateToDateObj(new_date);
            if (doi != this._state_.doi) { this._state_.doi = doi;
                if ("doiChanged" in this._listeners_) { this._listeners_.doiChanged("doiChanged", doi); }
            }
        }
    });

    Object.defineProperty(ToolLocationsManager.prototype, "id", { configurable:false, enumerable:false,
        get:function() { return this._state_.id; },
        set:function(id) { this._state_.id = id; }
    });

    Object.defineProperty(ToolLocationsManager.prototype, "variety", { configurable:false, enumerable:true, 
        get:function() { return this._state_.variety; },
        set:function(variety) { 
            if (variety != this._state_.variety) { this._state_.variety = variety;
                if ("varietyChanged" in this._listeners_) { this._listeners_.varietyChanged("varietyChanged", variety); }
            }
        }
    });

    Object.defineProperty(ToolLocationsManager.prototype, "coords", { configurable:false, enumerable:false, get:function() { return [ this._state_.lat, this._state_.lng ]; } });
    Object.defineProperty(ToolLocationsManager.prototype, "address", { configurable:false, enumerable:false, get:function() { return this._state_['address']; } });
    Object.defineProperty(ToolLocationsManager.prototype, "lat", { configurable:false, enumerable:false, get:function() { return this._state_.lat; }, });
    Object.defineProperty(ToolLocationsManager.prototype, "lng", { configurable:false, enumerable:false, get:function() { return this._state_.lng; }, });
    Object.defineProperty(ToolLocationsManager.prototype, "locations", { configurable:false, enumerable:false, get:function() { return this._locations_; }, });
    Object.defineProperty(ToolLocationsManager.prototype, "state", { configurable:false, enumerable:false, get:function() { return jQuery.extend({}, this._state_); }, });
    Object.defineProperty(ToolLocationsManager.prototype, "query", { configurable:false, enumerable:false,
        get:function() { var wrap = function(str) { return '"' + str + '"' };
            return { doi:wrap(this._state_.doi), location: { address:wrap(this._state_.address), lat:this._state_.lat, lng:this._state_.lng, id:wrap(this._state_.id) }, variety:wrap(this._state_.variety) } },
    });
    Object.defineProperty(ToolLocationsManager.prototype, "supported_listeners", { configurable:false, enumerable:false, writable:false, value: ["doiChanged", "locationChanged", "varietyChanged"] });
}

ToolLocationsManager.prototype.addListener = function(event_type, function_to_call) {
    var index = this.supported_listeners.indexOf(event_type);
    if (index >= 0) { this._listeners_[event_type] = function_to_call; }
}

ToolLocationsManager.prototype.addLocation = function(new_id, new_loc) {
    var loc_obj = jQuery.extend({}, new_loc);
    loc_obj.id = new_id;
    if (!('doi' in loc_obj) || loc_obj.doi == null) { loc_obj.doi = this.doi; }
    if (!('variety' in loc_obj) || loc_obj.variety == null) { loc_obj.variety = this.variety; }
    var validated = this.validate(loc_obj);
    var invalid = validated[0];
    if (invalid.length == 0) { loc_obj = validated[1]; this._locations_[loc_obj.id] = loc_obj; }
}

ToolLocationsManager.prototype.addLocations = function(locations) { var self = this; jQuery.each(locations, function(id, loc_obj) { self.addLocation(id, loc_obj); }); }

ToolLocationsManager.prototype.areDifferent = function(loc_obj_1, loc_obj_1) {
    return ( (loc_obj_1.address != loc_obj_2.address) ||
             (loc_obj_1.id != loc_obj_2.id) ||
             (loc_obj_1.lat != loc_obj_2.lat) ||
             (loc_obj_1.lng != loc_obj_2.lng) );
}

ToolLocationsManager.prototype.init = function(locations, default_location, default_doi, default_variety) {
    var loc_obj;
    var validated = [[], {}];

    if (default_doi) { this._state_.doi = this.tool.dateToDateObj(default_doi); }
    if (default_variety) { this._state_.variety = default_variety; }
    this.addLocations(locations);

    if (jQuery.type(default_location) === 'object') {
        validated = this.validate(default_location);
    } else if (jQuery.type(default_locaton) === 'string') {
        loc_obj = locations[default_locaton];
        if (!('doi' in loc_obj) || loc_obj.doi == null) { loc_obj.doi = this._state_.doi; }
        if (!('id' in loc_obj)) { loc_obj.id = default_location; }
        if (!('variety' in loc_obj) || loc_obj.variety == null) { loc_obj.variety = this._state_.variety; }
        validated =  this.validate(loc_obj);
    }
    if (validated[0].length == 0) { // gotta have a default !!!
        loc_obj = validated[1];
        this._locations_[loc_obj.id] = loc_obj;
        this._state_ = loc_obj; 
        if (loc_obj.id in locations) { delete locations[loc_obj.id]; }

    }
}

ToolLocationsManager.prototype.update = function(new_loc, fire_event) {
    var changed = [];
    if (!('doi' in new_loc) || new_loc.doi == null) { new_loc.doi = this._state_.doi }
    if (!('variety' in new_loc) || new_loc.variety == null) { new_loc.variety = this._state_.variety }
    var result = this.validate(new_loc);
    if (result[0]) { 
        var loc_obj = result[1];
        if (loc_obj.id != this._state_.id) { this._state_.id = loc_obj.id; changed.push('id'); }
        if (loc_obj.address != this._state_.address) { this._state_.address = loc_obj.address; changed.push("address");}
        if (loc_obj.doi != this._state_.doi) { this._state_.doi = loc_obj.doi; changed.push("doi"); }
        if (loc_obj.lat != this._state_.lat) { this._state_.lat = loc_obj.lat; changed.push("lat"); }
        if (loc_obj.lng != this._state_.lng) { this._state_.lng = loc_obj.lng; changed.push("lng"); }
        if (loc_obj.variety != this._state_.variety) { this._state_.variety = loc_obj.variety; changed.push("variety"); }
    }
    if (fire_event !== false && changed && "locationChanged" in this._listeners_) { this._listeners_.locationChanged("locationChanged", this.state, changed); }
}

ToolLocationsManager.prototype.updateDOI = function(new_date) {
    var doi = this.tool.dateToDateObj(new_date);
    this._state_.doi = doi; this._locations_[this._state_.id].doi = doi;
}

ToolLocationsManager.prototype.validate = function(new_loc) {
    var loc_obj = { id:null, address:null, doi:null, lat:null, lng:null, variety:null }
    var invalid = [ ];
    if ("key" in new_loc && jQuery.type(new_loc.key) === 'string') { loc_obj.id = new_loc.key;
    } else if ("id" in new_loc && jQuery.type(new_loc.id) === 'string') { loc_obj.id = new_loc.id; 
    } else { invalid.push("id"); }
    if ("address" in new_loc && jQuery.type(new_loc.address) === 'string') { loc_obj.address = new_loc.address; } else { invalid.push("address"); }
    if ("coords" in new_loc) {
        if (Array.isArray(new_loc.coords) && new_loc.coords.length == 2) {
            if (jQuery.type(new_loc.coords[0]) === 'number') { loc_obj.lat = new_loc.coords[0]; loc_obj.lng = new_loc.coords[1]; } else { invalid.push("lat"); invalid.push("lng"); }
        } else { valid = false; }
    } else {
        if ("lat" in new_loc && jQuery.type(new_loc.lat) === 'number') { loc_obj.lat = new_loc.lat } else { invalid.push("lat"); }
        if ("lng" in new_loc && jQuery.type(new_loc.lng) === 'number') { loc_obj.lng = new_loc.lng } else {  invalid.push("lng"); }
    }
    if ("doi" in new_loc && new_loc.doi instanceof Date) { loc_obj.doi = new_loc.doi; } else {  invalid.push("doi"); }
    if ("variety" in new_loc && jQuery.type(new_loc.variety) === 'string') { loc_obj.variety = new_loc.variety; } else { invalid.push("variety"); }
    return [invalid, loc_obj]
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
// set state globals
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

var initializeToolManager = function() {
    jQuery.ajaxPrefilter(function(options, original_request, jqXHR) { jqXHR.original_request = original_request; });

    GRAPEHARD.wait_widget = jQuery().CsfToolWaitWidget();
    GRAPEHARD.dates = new ToolDatesManager(GRAPEHARD);
    GRAPEHARD.dates.init({{ season }}, {{ season_start_day }}, {{ season_end_day }}, '{{ default_doi }}', '{{ doi }}');

    GRAPEHARD.dates.error_callback = function(jq_xhr, status_text, error_thrown) {
        console.log('BUMMER : request for Dates : Error Thrown : ' + error_thrown);
        console.log('  request : ' + jq_xhr.original_request.uri);
        console.log('  status : ' + status_text);
        console.log('  jqXHR : ' + jq_xhr.readyState, + ' : ' + jq_xhr.status + ' : ' + jq_xhr.statusText);
        console.log('  response text : ' + jq_xhr.responseText);
        console.log('  response xml : ' + jq_xhr.responseXML);
        console.log('  headers : ' + jq_xhr.getAllResponseHeaders());
    }

    GRAPEHARD.dates.addListener("daysChanged", function(ev, days) { GRAPEHARD.dataChanged('days'); });
    GRAPEHARD.dates.upload_callback = function(uploaded_obj, status_text, jq_xhr) { GRAPEHARD.dates.days = uploaded_obj.days; }

    var default_location = { address:"{{ loc_address }}", doi:null, key:"{{ loc_key }}",
                             lat:{{ loc_lat }}, lng:{{ loc_lng }}, variety: "{{ default_variety }}" };
    var doi = GRAPEHARD.dates.dateToDateObj("{{ doi }}");
    default_location['doi'] = doi;
    var locations = {{ locations_js }};
    GRAPEHARD.locations = new ToolLocationsManager(GRAPEHARD);
    GRAPEHARD.locations.init(locations, default_location, doi, "{{ default_variety }}");

    GRAPEHARD.data = new ToolDataManager(GRAPEHARD);
    GRAPEHARD.data.error_callbacks.tempexts = function(jq_xhr, status_text, error_thrown) {
        console.log('BUMMER : request for Temp Extremes : Error Thrown : ' + error_thrown);
        jQuery.each(jq_xhr.original_request, function(key, value) { console.log("    " + key + " : " + value); });
        console.log('  request : ' + jq_xhr.original_request.uri);
        console.log('  status : ' + status_text);
        console.log('  jqXHR : ' + jq_xhr.readyState, + ' : ' + jq_xhr.status + ' : ' + jq_xhr.statusText);
        console.log('  response text : ' + jq_xhr.responseText);
        console.log('  response xml : ' + jq_xhr.responseXML);
        console.log('  headers : ' + jq_xhr.getAllResponseHeaders());
    }
    GRAPEHARD.data.error_callbacks.hardtemp = function(jq_xhr, status_text, error_thrown) {
        console.log('BUMMER : requset for Hardiness Temp : Error Thrown : ' + error_thrown);
        console.log('  request : ' + jq_xhr.original_request.uri);
        console.log('  status : ' + status_text);
        console.log('  jqXHR : ' + jq_xhr.readyState, + ' : ' + jq_xhr.status + ' : ' + jq_xhr.statusText);
        console.log('  response text : ' + jq_xhr.responseText);
        console.log('  response xml : ' + jq_xhr.responseXML);
        console.log('  headers : ' + jq_xhr.getAllResponseHeaders());
    }

    GRAPEHARD.data.addListener("hardtempChanged", function(ev, data) { GRAPEHARD.dataChanged('hardtemp'); });
    GRAPEHARD.data.upload_callbacks.hardtemp = function(uploaded_obj, status_text, jq_xhr) {
        GRAPEHARD.logObjectAttrs(uploaded_obj.hardtemp.dates);
        GRAPEHARD.dates.update(uploaded_obj.hardtemp.dates);
        GRAPEHARD.logObjectAttrs(uploaded_obj.hardtemp.location);
        var loc_obj = uploaded_obj.hardtemp.location;
        if (jQuery.type(loc_obj.variety) === 'undefined' && jQuery.type(uploaded_obj.hardtemp.variety) !== 'undefined') { loc_obj["variety"] = uploaded_obj.hardtemp.variety; }
        GRAPEHARD.locations.update(loc_obj, false);
        GRAPEHARD.data.updateHardtemp(uploaded_obj.hardtemp.data);
    }

    GRAPEHARD.data.addListener("tempextsChanged", function(ev, data) { GRAPEHARD.dataChanged('tempexts'); });
    GRAPEHARD.data.upload_callbacks.tempexts = function(uploaded_obj, status_text, jq_xhr) { GRAPEHARD.data.updateTempexts(uploaded_obj.tempexts.data.mint); }
}
initializeToolManager();
