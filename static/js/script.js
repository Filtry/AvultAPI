function reset_options() {
    // Get all <select> elements on the page
    var selects = document.querySelectorAll('select');
    
    // Iterate over each <select> element
    selects.forEach(function(select) {
        // Reset the options of the current <select> element
        select.options.length = 0;
    });
    
    return true;
}