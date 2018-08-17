var loadGrapeHardinessToolStyles = function() {
    var csftool_url, grapehard_url;
    var tool_server = jQuery('meta[name="toolserver"]').attr("content");
    if (typeof tool_server === 'undefined') {
        tool_server = jQuery('meta[name="toolserver"]').attr("value");
    }
    var index = tool_server.indexOf("grapehard");
    if (index > 0) {
        csftool_url = tool_server.replace("grapehard","csftool");
        grapehard_url = tool_server;
    } else {
        csftool_url = tool_server + "/csftool";
        grapehard_url = tool_server + "/grapehard";
    }

    var dependency;
    var element = jQuery("head");
    dependency = document.createElement('link');
    dependency.setAttribute("rel","stylesheet");
    dependency.setAttribute("type","text/css");
    dependency.setAttribute("href", csftool_url + "/style/csftool.css");
    element.append(dependency);

    dependency = document.createElement('link');
    dependency.setAttribute("rel","stylesheet");
    dependency.setAttribute("type","text/css");
    dependency.setAttribute("href", csftool_url + "/style/csftool-spinner.css");
    element.append(dependency);

    dependency = document.createElement('link');
    dependency.setAttribute("rel","stylesheet");
    dependency.setAttribute("type","text/css");
    dependency.setAttribute("href", csftool_url + "/style/csftool-jquery-ui.css");
    element.append(dependency);

    dependency = document.createElement('link');
    dependency.setAttribute("rel","stylesheet");
    dependency.setAttribute("type","text/css");
    dependency.setAttribute("href", csftool_url + "/style/location-dialog-2.0.css");
    element.append(dependency);

    dependency = document.createElement('link');
    dependency.setAttribute("rel","stylesheet");
    dependency.setAttribute("type","text/css");
    dependency.setAttribute("href", grapehard_url + "/style/grapehard.css");
    element.append(dependency);
}
loadGrapeHardinessToolStyles();
