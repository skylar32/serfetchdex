$(function() {
    $("#search-bar").autocomplete({
        source: function(request, response) {
            $.getJSON(
                "/suggest",
                {q: $("#search-bar").val()},
                response
            );
        },
        select: function(event, ui) {
            window.location.href = '/' + ui.item.type + '/' + ui.item.value;
        }
    });
});