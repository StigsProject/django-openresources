function location_widget(el) {
    widget = $('#widget-location');
    widget.insertAfter(el);
    widget.show();

    if (!widget.data('isInitialized')) {
        map = new OpenLayers.Map (widget.find('.map').get(0), {
            controls:[
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.ScaleLine(),
                //new OpenLayers.Control.LayerSwitcher(),
                new OpenLayers.Control.MousePosition(),
                new OpenLayers.Control.Attribution()],
            maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
                        maxResolution: 156543.0399,
            numZoomLevels: 19,
            units: 'm',
            projection: new OpenLayers.Projection("EPSG:900913"),
            //projection: new OpenLayers.Projection("EPSG:4326"),
            displayProjection: new OpenLayers.Projection("EPSG:4326")
        } );
        
        layer_osm = new OpenLayers.Layer.OSM.Mapnik("OpenStreetMap");
        layer_osm.attribution = 'Map ' + layer_osm.attribution;
        map.addLayer(layer_osm);
        
        layer_vector = new OpenLayers.Layer.Vector("Vectors", {
            projection: new OpenLayers.Projection("EPSG:4326"),
        });         
        map.addLayer(layer_vector);
        
        var style = {
            externalGraphic: MEDIA_URL + "images/marker.png",
            graphicWidth: 21,
            graphicHeight: 25,
            graphicXOffset: -10,
            graphicYOffset: -25,
            graphicTitle: 'Current Location',
            cursor: 'pointer',
            graphicOpacity:0.7
        }
        
        var marker = null;
        var lonLat = new OpenLayers.LonLat(16.35, 48.2).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
        
        var value = $(el).html();
        if (value.startsWith("lonlat:")) {
          try {
              value = value.substring(7);
              value = value.split(",");
              lonLat = new OpenLayers.LonLat(parseFloat(value[0]), parseFloat(value[1])).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
              marker = new OpenLayers.Feature.Vector(
                 new OpenLayers.Geometry.Point(parseFloat(value[0]), parseFloat(value[1])).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()),
                 {title: 'Location'},
                 style);
              layer_vector.addFeatures([marker]);
           }
           catch(ex) {
                // fail silently in case of parse error
           }
        }
        
        map.setCenter (lonLat, 4);
        
        /*
        var control = new OpenLayers.Control.DrawFeature(layer_vector,
                            OpenLayers.Handler.Point, {
                                featureAdded: function(feature) {
                                        if (marker) {
                                            layer_vector.destroyFeatures([marker]);
                                        }
                                        marker = feature;
                                        
                                        p2 = feature.geometry.transform(map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
                                        $(el).html('lonlat:' + p2.x + ',' + p2.y);
                                    }
                                });
        */
        
        var control = new OpenLayers.Control();
        OpenLayers.Util.extend(control, {
            draw: function () {
                // this Handler.Box will intercept the shift-mousedown
                // before Control.MouseDefault gets to see it
                this.click_handler = new OpenLayers.Handler.Click( control, {
                     //pixelTolerance: 20,
                    click: function(ev){
                        lonLat = this.map.getLonLatFromPixel(ev.xy);
                        if (!lonLat) { 
                            // map has not yet been properly initialized
                            return;
                        }    
                        if (this.displayProjection) {
                            lonLat.transform(this.map.getProjectionObject(), 
                                             this.displayProjection );
                        }      
                        $(el).html('lonlat:' + lonLat.lon + ',' + lonLat.lat);
                        
                        if (marker) {
                             layer_vector.destroyFeatures([marker]);
                        }
                         marker = new OpenLayers.Feature.Vector(
                             new OpenLayers.Geometry.Point(lonLat.lon, lonLat.lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()),
                             {title: 'Location'},
                             style);
                         layer_vector.addFeatures([marker]);
                    }});
                this.click_handler.activate();
            }
        });
        map.addControl(control);
        control.activate();         
        
        widget.data('isInitialized', true);
    }	
}

function choice_widget(el, key) {
    var widget = $('<div class="widget">loading choices...</div>');
    widget.insertAfter(el);
    widget.show();

    $.getJSON('/resources/tag/' + key + '/choices.json',function(data) {
        var ul = $('Existing Values: <select><option value="">-</option></select>');
        for (var i=0; i<data.choices.length; i++) {
           ul.append('<option value="' + data.choices[i] + '">' + data.choices[i] + '</option>');
        }
        widget.html('');
        widget.append(ul);
        
        ul.change(function(ev) {
            $(el).val(ul.val());
        });
    });
}

function resource_choice(el, key) {
    var widget = $('<div class="widget">loading choices...</div>');
    widget.insertAfter(el);
    widget.show();

    $.getJSON('/resources/choices.json',function(data) {
        var ul = $('Resource: <select><option value="">-</option></select>');
        for (var i=0; i<data.choices.length; i++) {
           ul.append('<option value="' + data.choices[i] + '">' + data.choices[i] + '</option>');
        }
        widget.html('');
        widget.append(ul);
        
        ul.change(function(ev) {
            $(el).val(ul.val());
        });
    });
}

var editor_lookup = {
    'location': location_widget,
    'activity': choice_widget,
    'lang': choice_widget,
    'mode_of_production': choice_widget,
    'mode_of_access': choice_widget,
    'mode_of_distribution': choice_widget,
    'decisionmaking': choice_widget,
    'motivation': choice_widget,
    'category': choice_widget,
    'spatial_unit': choice_widget,
    'organizational_unit': choice_widget,
    'organizational_type': choice_widget,
    'organisationsform': choice_widget,
    'ownership': choice_widget,
    'license': choice_widget,
    'part_of': resource_choice,
    'available_at': resource_choice,
    'hosted_by': resource_choice
}

jQuery(function($) {
    $('#id_shortname, #id_view-shortname').change(function() {
        this._dirty = true;
    });
    $('#id_shortname, #id_view-shortname').each(function() {
        if (this.value) this._dirty = true;
    });
    $('#id_name, #id_view-name').keyup(function() {
        var el = $('#id_shortname, #id_view-shortname');
        if (! el[0]._dirty) {
            el.val(URLify($(this).val(), 100));
        }
    });
    
    /*
    $('input[type=text][id$=-key]').change(function() {
        var key_field = $(this);
        var key = key_field.val();
                
        var widget = editor_lookup[key];
        if (widget) {
            var value_field_id = this.id.substring(0, this.id.indexOf('-key')) + '-value';
            var value_field = $('#' + value_field_id);
            
            value_field.after('<div class="value-widget">' + widget + '</div>');           
            //value_field.css({'display': 'none'});
        }
    });
    */
    
    $('textarea').focus(function() {
        $('.widget').hide();
        var key = $(this).parents('tr').find('td input[name$="-key"]').val();
        var widget_func = editor_lookup[key];
        if (widget_func) {
            widget_func(this, key);
        }
        
    });  
    
    $('.popular-tags').change(function(ev) {
    	var $table = $(this).parents('.edit-table')
        $table.find('tr.extra td.edit-key input[type=text]').val($(this).val());
        ev.preventDefault();
        $table.find('tr.extra td.edit-value textarea')[0].focus();
    });  
});

/*
TODO:
http://djangosnippets.org/snippets/1389/

function updateElementIndex(el, prefix, ndx) {
		var id_regex = new RegExp('(' + prefix + '-\\d+)');
		var replacement = prefix + '-' + ndx;
		if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
		if (el.id) el.id = el.id.replace(id_regex, replacement);
		if (el.name) el.name = el.name.replace(id_regex, replacement);
	}

    function addForm(btn, prefix) {
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        var row = $('.dynamic-form:first').clone(true).get(0);
        $(row).removeAttr('id').insertAfter($('.dynamic-form:last')).children('.hidden').removeClass('hidden');
        $(row).children().not(':last').children().each(function() {
    	    updateElementIndex(this, prefix, formCount);
    	    $(this).val('');
        });
        $(row).find('.delete-row').click(function() {
    	    deleteForm(this, prefix);
        });
        $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
        return false;
    }

    function deleteForm(btn, prefix) {
        $(btn).parents('.dynamic-form').remove();
        var forms = $('.dynamic-form');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
    	    $(forms.get(i)).children().not(':last').children().each(function() {
    	        updateElementIndex(this, prefix, i);
    	    });
        }
        return false;
    }
*/
