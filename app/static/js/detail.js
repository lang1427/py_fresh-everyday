
$('.detail_tab li').on('click', function () {
    $(this).addClass('active').siblings().removeClass('active')
    if ($(this).prop('id') == 'tag_detail') {
        $('#tab_detail').show()
        $('#tab_comment').hide()
    } else {
        $('#tab_comment').show()
        $('#tab_detail').hide()
    }
})

var $add_x = $('#add_cart').offset().top;
var $add_y = $('#add_cart').offset().left;

var $to_x = $('#show_count').offset().top;
var $to_y = $('#show_count').offset().left;

var updateTotalPrice = function () {
    var count = parseInt($('.num_show').val())
    var price = parseFloat($('.show_pirze em').text())
    var totalPrice = (count * price).toFixed(2) + '元'
    $('.total em').text(totalPrice)
}

$('.add').on('click', function () {
    $(".num_show").val(parseInt($(".num_show").val()) + 1)
    updateTotalPrice()
})

$('.minus').on('click', function () {
    var input_val = parseInt($(".num_show").val())
    if (input_val <= 1) {
        return
    }
    $(".num_show").val(input_val - 1)
    updateTotalPrice()
})

var num_show = $(".num_show").val()
$('.num_show').on('blur', function () {
    count = $(this).val()
    if (isNaN(count) || count.trim().length == 0 || parseInt(count) <= 0) {
        count = 1
    }
    $(this).val(parseInt(count))
    updateTotalPrice()
})

$('#add_cart').click(function () {
    $(".add_jump").css({ 'left': $add_y + 80, 'top': $add_x + 10, 'display': 'block' })
    $.ajax({
        url: "/cart/add",
        type: "post",
        data: {
            good_id: $("#good_id").val(),
            good_count: $(".num_show").val(),
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
        },
        async: false,
        success: function (data) {
            if (data.res) {
                $(".add_jump").stop().animate({
                    'left': $to_y + 7,
                    'top': $to_x + 7
                },
                    "fast", function () {
                        $(".add_jump").fadeOut('fast', function () {
                            $('#show_count').html(data.cart_len);
                        });
                    });
            } else {
                alert(data.msg)
            }
        }
    })
})