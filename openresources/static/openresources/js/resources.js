jQuery(function($) {
    $('form.autosubmit button').hide();
    $('form.autosubmit select').change(function(ev) {
        $(this).parents('form.autosubmit').submit();
    });
    $('.toggle.off').next().hide();
    $('.toggle').click(function(event) {
        $this = $(this);
        $this.next().toggle();
        $this.toggleClass('on');
        $this.toggleClass('off');
    });

    function updateLocation(position) {
      // Show a map centered at (position.coords.latitude, position.coords.longitude).
        alert(position.coords.latitude);
    }
    if (navigator.geolocation) {
        $('.uselocationbutton').click(function(){
            navigator.geolocation.getCurrentPosition(updateLocation, function(error) {
                alert("Error getting position: " + error.message);            
            });
        });
    }
    else {
        $('.uselocationbutton').addClass('disabled');
        $('.uselocationbutton').attr('disabled','disabled');
    }
});
