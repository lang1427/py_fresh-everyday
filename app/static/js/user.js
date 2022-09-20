$(function () {

    $('.oper_btn').each(function () {
        var status = $(this).attr('status')
        if (status == '4') {
            $(this).text('去评价')
        } else if (status == '5') {
            $(this).text('已完成')
        }
    })

    $('.oper_btn').on('click', function () {
        var trade_no = $(this).attr('trade_no')
        if ($(this).attr('status') == "1") {
            $.ajax({
                url: "/order/pay",
                method: "post",
                data: {
                    trade_no: trade_no,
                    csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
                },
                success: function (data) {
                    if (data.res) {
                        window.open(data.msg)
                        $.ajax({
                            url: "/order/query",
                            method: "post",
                            data: {
                                trade_no: trade_no,
                                csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()
                            },
                            success: function (data) {
                                if (data.res) {
                                    alert('支付成功')
                                    window.location.reload()
                                } else {
                                    alert('支付失败')
                                }
                            }
                        })
                    } else {
                        alert(data.msg)
                    }
                }
            })
        } else if ($(this).attr('status') == '4') {
            window.location.href = '/order/comment/' + trade_no
        } else {
            alert("该订单已支付过")
        }
    })
})