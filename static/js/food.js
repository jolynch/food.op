$(document).ready(function() {
    $('.recipe').each(function(i, node) {
        var id = $(node).attr('recipe-id');
        $.ajax({
            url:"/recipe/"+id,
            success: function(result) {
                $(node).html(result)
            }
        });
    })

    $('.upvote').click(function() {
        var item = $(this);
        var uid = item.attr('user-id');
        var rid = item.attr('recipe-id');
        $.post('/vote/up/' + uid + "/" + rid, function(data) {
            var p = item.parent();
            p.removeClass('btn-group')
            p.html("<div class='text-success'>Thank you</div>");
        });
    });

    $('.downvote').click(function() {
        var item = $(this);
        var uid = item.attr('user-id');
        var rid = item.attr('recipe-id');
        $.post('/vote/down/' + uid + "/" + rid, function(data) {
            var p = item.parent();
            p.removeClass('btn-group')
            p.html("<div class='text-success'>Thank you</div>");

        });
    });

    $('.remove').click(function() {
        var item = $(this);
        var uid = item.attr('user-id');
        var rid = item.attr('recipe-id');
        $.post('/vote/remove/' + uid + "/" + rid, function(data) {
            var p = item.parent();
            p.hide('slow', function(){ p.remove(); });
        });
    });

});
