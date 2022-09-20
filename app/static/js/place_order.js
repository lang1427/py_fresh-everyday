$('#order_btn').click(function () {

    var params = {
        sku_ids: $("#sku_ids").val(),
        addr_id: $("input[name='address']:checked").val(),
        pay_method: $('input[name="pay_style"]:checked').val(),
        csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
    }

    $.ajax({
        url: '/order/commit',
        method: "post",
        data: params,
        success: function (data) {
            if (data.res) {
                $('.popup_con').fadeIn('fast', function () {

                    setTimeout(function () {
                        $('.popup_con').fadeOut('fast', function () {
                            window.location.href = '/user/order/1';
                        });
                    }, 3000)

                });
            } else {
                alert(data.msg)
            }
        }
    })


});