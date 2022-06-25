function seen_notifications() {
    $.get("notifications_set_seen/", function(data) {
        $('.notifications').html(data.result);
    });
}

setTimeout("seen_notifications()", 2500);