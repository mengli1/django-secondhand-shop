//index.html

function type_btn(obj, set1, a_url) {
    typetext = $(obj).text();
    $(function () {
        $.ajax({
            type: 'post',
            url: '/index/',
            dataType: "json",
            data: {
                "type": typetext,
                "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val()
            },
            success: function (data) { //返回json结果
                body_data(data, set1, a_url);
            },
            error: function () {
                alert('1.网络错误，请稍后再试！\n2.如未登录，请先登录！');
            }
        });
    });
}

function body_data(data, set1, a_url) {
    $("#goods_index").empty();
    if (data.status === 'failed') {
        alert('1.网络错误，请稍后再试！\n2.如未登录，请先登录！');
    } else {
        $.each(data.data, function (i, item) {
            $("#goods_index").append("<div class=\"col-md-3 col-sm-6\">\n" +
                "                    <div class=\"thumbnail \">\n" +
                "                        <img data-src=\"holder.js/100%x200\" alt=\"100%x200\"\n" +
                "                             src=\"" + set1 + item.url + "\"\n" +
                "                             data-holder-rendered=\"true\" style=\"height: 200px; width: 100%; display: block;\">\n" +
                "                        <div class=\"caption\">\n" +
                "                            <h3 class=\"title_h3\">" + item.title + "</h3>\n" +
                "                            <p class=\"price_p\">￥" + parseFloat(item.price).toFixed(2) + "</p>\n" +
                "                            <p><a href=\"" + a_url + item.id + "\" class=\"btn btn-default\" role=\"button\">查看详情</a></p>\n" +
                "                        </div>\n" +
                "                    </div>\n" +
                "                </div>")
        })
    }
}

//gooddetail.html
function love_click(obj, s_url, sr_url, q_url, id) {
    var lstatus;
    if ($(obj).attr('src') === s_url) {
        lstatus = 1
    } else {
        $(obj).attr('src', s_url);
        lstatus = 0
    }
    $(function () {
        $.ajax({
            type: 'get',
            url: q_url,
            dataType: "json",
            data: {
                "id": id,
                "status": lstatus
            },
            success: function (data) { //返回json结果
                if (data.status === '1') {
                    alert("收藏成功");
                    $(obj).attr('src', sr_url);
                } else {
                    alert("取消收藏成功");
                    $(obj).attr('src', s_url);
                }
            },
            error: function () {
                alert('1.网络错误，请稍后再试！\n2.如未登录，请先登录！');
            }
        });
    });
}

function mes_click(obj, q_url, id) {
    var lstatus;
    var message = $(".mess").val();
    if ($(obj).text() === "留言") {
        lstatus = "mess"
    }
    $(function () {
        $.ajax({
            type: 'post',
            url: q_url,
            dataType: "json",
            data: {
                "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
                "id": id,
                "status": lstatus,
                "message": message
            },
            success: function (data) { //返回json结果
                alert('留言成功！');
                window.location.reload();
            },
            error: function () {
                alert('1.网络错误，请稍后再试！\n2.如未登录，请先登录！');
            }
        });
    });
}

function replay_click(obj) {
    $("#message").children("input:last").removeClass("mess");
    $(".message2").children("input").removeClass("mess");
    $("#message").attr("style", "display:none");
    $(".message2").attr("style", "display:none");
    $(obj).parent().parent().parent().parent().find(".message2").css("display", "");
    $(obj).parent().parent().parent().parent().find(".message2").find("input").addClass("mess");
}