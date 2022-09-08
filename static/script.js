$(document).ready(function () {
    /* When button is pressed open up pop-up form */
    $("#add_asset").click(function () {
        $('#add').modal('show');
    });

    /* When save is clicked, loop through array of inputs and add to DB */
    $("#save").click(function () {

        var textareaContent = $("#assets").val();
        var assets = textareaContent.split("\n");

        for (var i = 0; i < assets.length; i++) {
            $.ajax({
                url: '/asset',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ "symbol": assets[i] }),
                dataType: 'json'
            });
        }

        $('#add').modal('hide');
    });

    /* When button is pressed open up pop-up form */
    $("#remove_asset").click(function () {
        $('#del').modal('show');
    });

    /* When save is clicked, loop through array of inputs and add to DB */
    $("#remove").click(function () {

        var textareaContent = $("#rm_assets").val();
        var assets = textareaContent.split("\n");

        for (var i = 0; i < assets.length; i++) {
            $.ajax({
                url: '/asset/' + assets[i],
                type: 'DELETE'
            });
        }

        $('#del').modal('hide');
    });

    $("#update_assets").click(function () {
        $.ajax({
            url: '/update',
            type: 'GET'
        });
    });
});