$( function() {
    $( ".approvals" ).formset({
        prefix: 'approvals',
        formCssClass: 'dynamic-chaperones'
    });
    $( ".chaperones" ).formset({
        prefix: 'chaperones',
        formCssClass: 'dynamic-approvals'
    });
})
