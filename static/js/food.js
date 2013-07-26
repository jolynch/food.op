$(document).ready(function() {
    $('.recipe').each(function(i, node) {
        var id = $(node).attr('recipe-id');
        $.ajax({
            url:"/recipe/"+id,
            success: function(result) {
                $(node).html(result);
            }
        });
    })

    $('.create').click(function() {
        var item = $(this);
        var text = $('.create-user-field');
        if (text.val()) {
            $.post('/user/create/', {'username': text.val()}, function(data) {
                window.location.reload();
            });
        }
    });


    $('.delete').click(function() {
        var item = $(this);
        var userId = item.attr('user-id');
        var userName = item.attr('user-name');
        if (confirm("Are you sure you want to delete: " + userName)) {
            $.post('/user/delete/', {'user_id': userId}, function(data) {
                window.location.reload();
            });
        }
    });



    $('.upvote').click(function() {
        var item = $(this);
        var uid = item.attr('user-id');
        var rid = item.attr('recipe-id');
        $.post('/vote/up/' + uid + "/" + rid, function(data) {
            var p = item.parent();
            p.hide('slow', function() {
                p.removeClass('btn-group');
                p.html("<div class='text-success'>Thank you</div>");
                p.show();
            });
        });
    });

    $('.downvote').click(function() {
        var item = $(this);
        var uid = item.attr('user-id');
        var rid = item.attr('recipe-id');
        $.post('/vote/down/' + uid + "/" + rid, function(data) {
            var p = item.parent();
            p.hide('slow', function() {
                p.removeClass('btn-group');
                p.html("<div class='text-success'>Thank you</div>");
                p.show();
            });
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
