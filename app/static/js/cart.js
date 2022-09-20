
// 更新合计
function updateWhole() {
    var goods_count = 0, total_price = 0;
    if ($('.cart_list_td :checked').length != 0) {
        $('.cart_list_td :checked').each(function () {
            var count = parseInt($(this).parents('ul').find('.num_show').val())
            var amount = parseFloat($(this).parents('ul').find('.col07').text().replace("元", ""))
            goods_count += count
            total_price += amount
        })
    }
    $(".settlements .col03 em").text(total_price.toFixed(2))
    $(".settlements .col03 b").text(goods_count)
}
// 更新当前商品小计
function updateCurAmount($cur_ul) {
    good_count = parseInt($cur_ul.find('.num_show').val())
    good_price = parseFloat($cur_ul.find('.col05').text().replace("元", ""))
    cur_amount = (good_count * good_price).toFixed()
    $cur_ul.find('.col07').text(cur_amount + "元")
}

// 全选按钮 操作
$(".settlements :checkbox").on('click', function () {
    var checked = $(this).prop("checked")
    $(".cart_list_td :checkbox").prop("checked", checked)
    updateWhole()
})
// 单选
$(".cart_list_td :checkbox").on('click', function () {
    var cart_checkbox = $(".cart_list_td :checkbox").length
    var cart_checkedbox = $(".cart_list_td :checked").length
    if (cart_checkbox == cart_checkedbox) {
        $(".settlements :checkbox").prop("checked", true)
    } else {
        $(".settlements :checkbox").prop("checked", false)
    }
    updateWhole()
})


$('.add').on('click', function () {
    var params = {
        good_id: $(this).next().attr("good_id"),
        good_count: parseInt($(this).next().val()) + 1,
        csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
    }
    var _this = $(this)
    $.ajax({
        url: "/cart/update",
        type: "post",
        data: params,
        success: function (data) {
            if (data.res) {
                $(".total_count em").text(data.cart_total)
                _this.next().val(parseInt(_this.next().val()) + 1)
                updateCurAmount(_this.parents('ul'))
                if (_this.parents('ul').find(':checkbox').prop("checked")) {
                    updateWhole()
                }
            } else {
                alert(data.msg)
            }
        }
    })
})
$('.minus').on('click', function () {
    var input_val = parseInt($(this).prev().val())
    if (input_val < 2) {
        alert("购物车数量不能少于1")
        return false
    }
    var params = {
        good_id: $(this).prev().attr("good_id"),
        good_count: parseInt($(this).prev().val()) - 1,
        csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
    }
    var _this = $(this)
    $.ajax({
        url: "/cart/update",
        type: "post",
        data: params,
        success: function (data) {
            if (data.res) {
                $(".total_count em").text(data.cart_total)
                _this.prev().val(parseInt(_this.prev().val()) - 1)
                updateCurAmount(_this.parents('ul'))
                if (_this.parents('ul').find(':checkbox').prop("checked")) {
                    updateWhole()
                }
            } else {
                alert(data.msg)
            }
        }
    })
})
var cur_cart_count = 0
$('.num_show').on('focus', function () {
    cur_cart_count = $(this).val()
}).on('blur', function () {
    var count = $(this).val()
    if (isNaN(count) || count.trim().length == 0 || parseInt(count) <= 0) {
        $(this).val(cur_cart_count)
        return
    }
    count = parseInt($(this).val())
    var params = {
        good_id: $(this).attr("good_id"),
        good_count: count,
        csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
    }
    var _this = $(this)
    $.ajax({
        url: "/cart/update",
        type: "post",
        data: params,
        success: function (data) {
            if (data.res) {
                $(".total_count em").text(data.cart_total)
                _this.val(count)
                updateCurAmount(_this.parents('ul'))
                if (_this.parents('ul').find(':checkbox').prop("checked")) {
                    updateWhole()
                }
            } else {
                alert(data.msg)
                _this.val(cur_cart_count)
            }
        }
    })
})
$('.col08 a').on('click', function () {
    var params = {
        good_id: $(this).parents('ul').find('.num_show').attr("good_id"),
        csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
    }
    var _this = $(this)
    $.ajax({
        url: "/cart/del",
        type: "post",
        data: params,
        success: function (data) {
            if (data.res) {
                $("#show_count").text(data.cart_len)
                $(".total_count em").text(data.cart_total)
                _this.parents('ul').remove()
                updateWhole()
            } else {
                alert(data.msg)
            }
        }
    })
})