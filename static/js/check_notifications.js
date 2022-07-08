function check_notifications() {
    // Пока такой вот костыль, лучше не придумал
    $.get("../../../../../notifications_check/", function(data) {
        $('.topmenu').html(data.result);
    });
}
window.onload = check_notifications();
setInterval("check_notifications()", 10000);