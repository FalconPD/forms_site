$( function() {
    $( ".datetimepicker" ).datetimepicker({ //make datetimepickers show up
        controlType: 'select',
        onLine: true,
        timeFormat: 'hh:mm tt'});
    $( ".chaperones" ).formset(); // make it so that we can add/del chaperones
})
