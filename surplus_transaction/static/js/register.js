$(function () {

    var error_name = false;
    var error_password = false;
    var error_check_password = false;
    var error_email = false;
    var error_check = false;


    $('#username').blur(function () {
        check_user_name();
    });

    $('#password').blur(function () {
        check_pwd();
    });

    $('#con_password').blur(function () {
        check_cpwd();
    });

    $('#email').blur(function () {
        check_email();
    });

    $('#checkbox').click(function () {
        if ($(this).is(':checked')) {
            error_check = false;
            $(this).siblings('span').hide();
        } else {
            error_check = true;
            $(this).siblings('span').html('请勾选同意');
            $(this).siblings('span').show();
        }
    });


    function check_user_name() {
        var len = $('#username').val().length;
        if (len < 5 || len > 20) {
            $('#username').next().html('请输入5-20个字符的用户名')
            $('#username').next().show();
            error_name = true;
        } else {
            $('#username').next().hide();
            error_name = false;
        }
    }

    function check_pwd() {
        var len = $('#password').val().length;
        if (len < 8 || len > 20) {
            $('#password').next().html('密码最少8位，最长20位')
            $('#password').next().show();
            error_password = true;
        } else {
            $('#password').next().hide();
            error_password = false;
        }
    }


    function check_cpwd() {
        var pass = $('#password').val();
        var cpass = $('#con_password').val();

        if (pass != cpass) {
            $('#con_password').next().html('两次输入的密码不一致')
            $('#con_password').next().show();
            error_check_password = true;
        } else {
            $('#con_password').next().hide();
            error_check_password = false;
        }

    }

    function check_email() {
        var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;

        if (re.test($('#email').val())) {
            $('#email').next().hide();
            error_email = false;
        } else {
            $('#email').next().html('你输入的邮箱格式不正确')
            $('#email').next().show();
            error_check_password = true;
        }

    }


    $('#signin-form').submit(function () {
        check_user_name();
        check_pwd();
        check_cpwd();
        check_email();

        if (error_name == false && error_password == false && error_check_password == false && error_email == false && error_check == false) {
            return true;
        } else {
            return false;
        }

    });


})