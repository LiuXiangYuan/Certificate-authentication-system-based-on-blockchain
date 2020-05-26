function check_phone(phone) {
    var reg =/^0?1[3|4|5|6|7|8][0-9]\d{8}$/;
    if(!reg.test(phone)){
        alert("手机号码格式不正确");
        return false;
    }
    return true;
}

function check_email(email) {
    var reg = /^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/;
    if(!reg.test(email)){
        alert("邮箱格式不正确");
        return false;
    }
    return true;
}

