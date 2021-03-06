window.onload = function () {

     $('.basket_items').on('click', 'input[type=number]', function () {
        let t_href = event.target;

        $.ajax({
            url: "/basket/edit/" + t_href.name + "/" + t_href.value + "/",

            success: function (data) {
                $('.basket_items').html(data.result);

            },

        });
        return false;
    });

    let _quantity, _price, orderitem_num, delta_quantity, orderitem_quantity, delta_cost;
    let quantity_arr = [];
    let price_arr = [];

    let TOTAL_FORMS = parseInt($('input[name="orderitems-TOTAL_FORMS"]').val());

    let order_total_quantity = parseInt($('.order_total_quantity').text()) || 0;
    let order_total_cost = parseFloat($('.order_total_cost').text().replace(',', '.')) || 0;


    for (let i = 0; i < TOTAL_FORMS; i++) {
        _quantity = parseInt($('input[name="orderitems-' + i + '-quantity"]').val());
        _price = parseFloat($('.orderitems-' + '-price').text().replace(',', '.'));
        quantity_arr[i] = _quantity;
        if (_price) {
            price_arr[i] = _price;
        } else {
            price_arr[i] = 0;
        }
    }

    $('.order_form').on('click', 'input[type=number]', function () {
        let target = event.target;
        orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-quantity', ''));
        if (price_arr[orderitem_num]){
            orderitem_quantity = parseInt(target.value);
            delta_quantity = orderitem_quantity - quantity_arr[orderitem_num];
            quantity_arr[orderitem_num] = orderitem_quantity;
            order_summary_update(price_arr[orderitem_num], delta_quantity);
        }
    });

    $('.order_form').on('click', 'input[type=checkbox]', function () {
        let target = event.target;
        alert(target)
        orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-quantity', ''));
        if (target.checked) {
            delta_quantity = -quantity_arr[orderitem_num];
        } else {
            delta_quantity = quantity_arr[orderitem_num];
        }
        order_summary_update(price_arr[orderitem_num], delta_quantity)

    });

    function order_summary_update(orderitem_price, delta_quantity) {
        delta_cost = price_arr[orderitem_num] * delta_quantity;
        order_total_cost = Number((order_total_cost + delta_cost).toFixed(2));
        order_total_quantity = order_total_quantity + delta_quantity;

        $('.order_total_quantity').html(order_total_quantity.toString());
        $('.order_total_cost').html(order_total_cost.toString());
    }


    $('.formset_row').formset({

        addText: '???????????????? ??????????????',
        deleteText: '??????????????',
        prefix: 'orderitems',
        removed: deleteOrderItem
    });

    $('.order_form select').change(function () {
        let target = event.target;
        alert('1')
        orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-quantity', ''));
        let product_id = target.options[target.selectedIndex].value;
        alert(product_id)
        if (product_id) {
            $.ajax({
                url: '/order/product/price/' + product_id + '/',
                success: function (data) {
                    if (data.price) {
                        price_arr[orderitem_num] = data.price;
                        if (isNaN(quantity_arr[orderitem_num])) {
                            quantity_arr[orderitem_num] = 0;
                        }
                        let price_string = '<span>' + data.price.toString().replace('.', ',') + '</span>';
                        let current_tr = $('.order_form table').find('tr:eq(' + (orderitem_num + 1) + ')');
                        current_tr.find('td:eq(2)').html(price_string);
                    }
                }
            })
        }
    });


    function deleteOrderItem(row) {
        let target_name = row[0].querySelector('input[type=number]').name;
        orderitem_num = parseInt(target_name.replace('orderitems-', '').replace('-DELETE', ''));
        delta_quantity = -quantity_arr[orderitem_num]
        order_summary_update(price_arr[orderitem_num], delta_quantity)
    }

}