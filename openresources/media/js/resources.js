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
});
