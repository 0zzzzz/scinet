function favorite_change() {
    console.log('Начало функции');
    let favorite = $(this);
    let post_id = favorite.data('id');
    $.ajax({
        url: "/posts/favorites/change/" + post_id,
        type:  'post',

        success: function () {
            console.log('Смена картинки');
            if (favorite.attr('data-action') === 'on') {
                favorite.attr('src', '/static/img/star-off.svg');
                favorite.attr('data-action', 'off')
            }
            else{
                favorite.attr('src', '/static/img/star-on.svg');
                favorite.attr('data-action', 'on')
            }
        },
        error: function () {
            alert('Всё сломал!');
        }
    });
    return false;
}

$(function ()
    {
        document.getElementById('favorite').onclick = favorite_change;
    });