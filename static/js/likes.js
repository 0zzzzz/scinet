let request = null;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Настройка AJAX
$(function () {
    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });
});

function like() {
    let like = $(this);
    let type = like.data('type');
    let pk = like.data('id');
    let action = like.data('action');
    let dislike = like.next();

    if (request) {
        request.abort();
    }


    request = $.ajax({
        url: "/posts/" + type + "/" + pk + "/" + action + "/",
        type: 'POST',
        data: {'obj': pk},

        success: function (json) {
            like.find("[data-count='like']").text(json.like_count);
            dislike.find("[data-count='dislike']").text(json.dislike_count);
        }
    });

    return false;
}

function dislike() {
    let dislike = $(this);
    let type = dislike.data('type');
    let pk = dislike.data('id');
    let action = dislike.data('action');
    let like = dislike.prev();

    if (request) {
        request.abort();
    }

    request = $.ajax({
        url: "/posts/" + type + "/" + pk + "/" + action + "/",
        type: 'POST',
        data: {'obj': pk},

        success: function (json) {
            dislike.find("[data-count='dislike']").text(json.dislike_count);
            like.find("[data-count='like']").text(json.like_count);
        },
        error: function () {
            alert('Всё сломал!');
        }
    });

    return false;
}

// Подключение обработчиков
$(function () {
    $('[data-action="like"]').click(like);
    $('[data-action="dislike"]').click(dislike);
});
