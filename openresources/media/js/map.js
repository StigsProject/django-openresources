
var lat=48.2;
var lon=16.35;
var zoom=12;

var map;
var select;

function get_icon(feature, mapping){
	if (feature.data.tags[mapping['key']]) {
		if (mapping['value']) {
			for (var i=0; i<feature.data.tags[mapping['key']].length; i++) {
				if (feature.data.tags[mapping['key']][i] == mapping['value']) {
	                return {icon: mapping['icon'], tag: mapping['key'] + ' = ' + mapping['value']};
				}
			}
		}
		else {
            return {icon: mapping['icon'], tag: mapping['key'] + ' = *'};
		}
	}  
	return null;
}

function get_icons(feature) {
	var icons = [];
	var first_is_subicon = false;
	for (var i=0; i<icon_mappings.length; i++) {
	    var mapping = icon_mappings[i];
	    if (icons.length == 0) {
	    	// if we find the first icon, remeber if it should be a subicon
	    	first_is_subicon = mapping['subicon_only'];
	    }
	    if (feature.cluster) {
	        for (var j=0; j<feature.cluster.length; j++) {
	            var icon = get_icon(feature.cluster[j], mapping)
	            if (icon) {
	                icons.push(icon);
	                break;
	            }
	        }
	    }
	    else {
	        var icon = get_icon(feature, mapping)
	        if (icon) {
	            icons.push(icon);
	        }
	    }
	}
	if (first_is_subicon || icons.length == 0) {
		icons.splice(0, 0, {icon: DEFAULT_ICON});
	}
	return icons;
}

OpenLayers.Layer.MapsWithoutBorders = OpenLayers.Class(OpenLayers.Layer.OSM, {
    /**
     * Constructor: OpenLayers.Layer.MapsWithoutBorders
     *
     * Parameters:
     * name - {String}
     * options - {Object} Hashtable of extra options to tag onto the layer
     */
    initialize: function(name, options) {
        options = OpenLayers.Util.extend({
            numZoomLevels: 19,
            buffer: 0,
            transitionEffect: "resize",
            base_url: 'http://tiles.mapswithoutborders.eu/',
            style: 'default'
        }, options);
        this.noborders_urls = [
            options.base_url + options.style + "/${z}/${x}/${y}.png"
        ];
        this.osm_urls = [
            "http://a.tile.openstreetmap.org/${z}/${x}/${y}.png",
            "http://b.tile.openstreetmap.org/${z}/${x}/${y}.png",
            "http://c.tile.openstreetmap.org/${z}/${x}/${y}.png"
        ];
        this.noborders_max_zoom = 6;
        var newArguments = [name, this.osm_urls, options];
        OpenLayers.Layer.OSM.prototype.initialize.apply(this, newArguments);

        this.mwob_attribution = 'Map CC-by-SA <a href="http://www.mapswithoutborders.eu/" target="_blank">Mapswithoutborders.eu</a>, Data by <a href="http://www.naturalearthdata.com/" target="_blank">Natural Earth</a> &amp; CC-by-SA <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a>';
        this.osm_attribution = 'Map Data CC-by-SA <a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a>';
        this.attribution = this.mwob_attribution;
    
        this.events.register("moveend",this,function(event){
            if (event.zoomChanged && this.map) {
                //alert("zoom changed");
                if (this.map.getZoom() > this.noborders_max_zoom) {
                    this.attribution = this.osm_attribution;
                }
                else {
                    this.attribution = this.mwob_attribution;
                }
                this.map.events.triggerEvent('changelayer',{property:'attribution'});
            }
        });

    },

    getURL: function (bounds) {
        var res = this.map.getResolution();
        var xyz = {};
        xyz.x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        xyz.y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
        xyz.z = this.map.getZoom() + this.zoomOffset;

        // trunk
        //var xyz = this.getXYZ(bounds);

        var url = this.noborders_urls[0];
        if (xyz.z > this.noborders_max_zoom) {
            url = this.osm_urls;
            if (url instanceof Array) {
                var s = '' + xyz.x + xyz.y + xyz.z;
                url = this.selectUrl(s, url);
            }
        }
        
        return OpenLayers.String.format(url, xyz);
    },

    CLASS_NAME: "OpenLayers.Layer.MapsWithoutBorders"
});


function init_map() {
	
    map = new OpenLayers.Map ("map", {
        controls:[
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.PanZoomBar(),
            new OpenLayers.Control.ScaleLine(),
            new OpenLayers.Control.MousePosition(),
            new OpenLayers.Control.Attribution()],
        maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
                    maxResolution: 156543.0399,
        numZoomLevels: 19,
        units: 'm',
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326")
    } );

    //layer_osm = new OpenLayers.Layer.OSM.Mapnik("OpenStreetMap");
    //layer_osm.attribution = 'Map ' + layer_osm.attribution;
    //map.addLayer(layer_osm);
    
    layer_noborders = new OpenLayers.Layer.MapsWithoutBorders("Maps Without Borders");
    //layer_noborders.attribution = 'Map ' + layer_osm.attribution;
    map.addLayer(layer_noborders);
    
    var style = new OpenLayers.Style({
    	
        
        icon: '${icon}',
        mask: '${mask}',
        subicons: '${subicons}',
        subicontitles: '${subicontitles}',
        iconBaseURL: MEDIA_URL,
        subiconmask: 'openresources/map_marker/subicon_mask.png',
        zoomBox: '${zoomBox}',
        
        iconText: '${iconText}',
        
        iconXOffset: '${iconXOffset}',
        iconYOffset: '${iconYOffset}',

        graphicTitle: '${title}',
        graphicZIndex: 0,
        cursor: 'pointer',
        graphicOpacity:0.8,
        
        // fallback for non-svg browsers
        externalGraphic: '${externalGraphic}',
        graphicWidth: 20,
        graphicHeight: 20,
        graphicXOffset: -10,
        graphicYOffset: -20
    },{
        context: {
            title: function(feature) {
                return (feature.cluster) ? feature.cluster.length + ' resources' : feature.data.title;
            },
            externalGraphic: function(feature) {
                return MEDIA_URL + get_icons(feature)[0].icon;
            },
            icon: function(feature) {
                return get_icons(feature)[0].icon;
            },
            iconText: function(feature) {
                return (feature.cluster) ? feature.cluster.length : '';
            },
            mask: function(feature) {
                return 'openresources/map_marker/' + ((feature.cluster) ? 'cluster_mask.png' : 'marker_mask.png');
            },
            subicons: function(feature) {
            	var iconstr = "";
                var icons = get_icons(feature);
                icons.splice(0,1);
                for (var i=0; i<icons.length; i++) {
                    iconstr += icons[i].icon + '|';
                }
                return iconstr;
            },
            subicontitles: function(feature) {
            	var titles = "";
                var icons = get_icons(feature);
                icons.splice(0,1);
                for (var i=0; i<icons.length; i++) {
                	titles += icons[i].tag + '|';
                }
                return titles;
            },
            zoomBox: function(feature) {
                return feature.cluster ? true : '';
            },
            iconXOffset: function(f) { return f.cluster ? 2 : 3 },
            iconYOffset: function(f) { return f.cluster ? 1 : 3 },
         }
    });
    
    var select_style = OpenLayers.Util.extend({}, style);
    select_style.graphicOpacity = 1.0;
    select_style.graphicZIndex = 1;

    // http://openflights.org/blog/2009/10/21/customized-openlayers-cluster-strategies/
    var strategy = new OpenLayers.Strategy.Cluster({distance: 8, threshold: 2});
    var strategy2 = new OpenLayers.Strategy.Cluster({distance: 30, threshold: 8});
    
    layer_vector = new OpenLayers.Layer.Vector("Vectors", {
        attribution: MAP_ATTRIBUTION,
        styleMap: new OpenLayers.StyleMap({
            "default": style,
            "select": select_style}),
        strategies: [strategy2, strategy],
        renderers: ['OpenResourcesRenderer', 'SVG', 'VML', 'Canvas'], //
        projection: new OpenLayers.Projection("EPSG:4326"),
        rendererOptions: {yOrdering: true}
    });
    
    map.addLayer(layer_vector);
    
    /*
    var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
    map.setCenter (lonLat, zoom);
*/

    select = new OpenLayers.Control.SelectFeature(layer_vector, {
        onSelect: function(feature) {
            var content = "";
            if (feature.cluster) {
            	var list = "";
            	var bounds = new OpenLayers.Bounds();
                for (var i=0; i < feature.cluster.length; i++) {
                	bounds.extend(feature.cluster[i].geometry.getBounds());
                    list += "<a href='" + feature.cluster[i].data.url + "'>"+feature.cluster[i].data.title + "</a><br />";
                }
                content += '<h4>' + feature.cluster.length + ' Resources ';
                content += '[<a href="#" onclick="select.unselectAll(); map.zoomToExtent(OpenLayers.Bounds.fromString(\'' + bounds.toBBOX() + '\'));">zoom</a>]</h4>';
                content += list;
            }
            else {
                content = "<a href='" + feature.data.url + "'>"+feature.data.title + "</a>";
            }
            popup = new OpenLayers.Popup.FramedCloud("infoWindow", 
                                     feature.geometry.getBounds().getCenterLonLat(),
                                     new OpenLayers.Size(100,100),
                                     content,
                                     null, true, onPopupClose);
            feature.popup = popup;
            map.addPopup(popup);
        },
        onUnselect: function(feature) {
            if (feature.popup) {
                map.removePopup(feature.popup);
                feature.popup.destroy();
                delete feature.popup;
            }
        }
    });
    map.addControl(select);
    select.activate();

    function onPopupClose(evt) {
        select.unselectAll();
    }

    if (CONTEXT.area) {
        var bounds = OpenLayers.Bounds.fromArray(CONTEXT.area);
        bounds = bounds.transform(map.displayProjection, map.projection)
        map.zoomToExtent(bounds);
        //map.zoomTo(4);
        //map.setCenter(new OpenLayers.LonLat(100,10));
    }
//    map.events.register('movestart', null, function(event){
//    	select.unselectAll();
//    })
}

function add_content(features, adjust_viewport) {
    layer_vector.addFeatures(features);
    if (adjust_viewport) {
	    var bounds = new OpenLayers.Bounds();
        for (var i=0; i<features.length; i++) {
            bounds.extend(features[i].geometry);
        }
        map.zoomToExtent(bounds);
	    if (features.length < 2) {
	    	// single feature would cause full zoom-in
            map.zoomTo(13);

	    }
    }
}

$(document).ready(function(){
    $.get(JSON_URL, function(data) {

        $('.map-loading').hide();
        
	    var geojson_format = new OpenLayers.Format.GeoJSON({
	        internalProjection: new OpenLayers.Projection("EPSG:900913"),
	        externalProjection: new OpenLayers.Projection("EPSG:4326")
	    });
	    
	    var features = geojson_format.read(data);
	    
	    if (features.length > 0) {
	    	add_content(features, !CONTEXT.area);
	    }

    });

    $('#map').show();
	init_map();


});

/*
    var control = new OpenLayers.Control.EditingToolbar(layer_vector);
    map.addControl(control);
    control.activate();
        
    var control = new OpenLayers.Control.DrawFeature(layer_vector, OpenLayers.Handler.Point);
    map.addControl(control);
    control.activate();
*/   
      
/*    
    var proj = new OpenLayers.Projection("EPSG:4326");
    
    var point = new OpenLayers.Geometry.Point(lon,lat).transform(proj, map.getProjectionObject());
    var pointFeature = new OpenLayers.Feature.Vector(point, {title: 'Marker 1'});
    
    var point2 = new OpenLayers.Geometry.Point(lon+0.01,lat+0.01).transform(proj, map.getProjectionObject());
    var pointFeature2 = new OpenLayers.Feature.Vector(point2, {title: 'Marker 2'});
    
    layer_vector.addFeatures([pointFeature,pointFeature2]);
*/      
