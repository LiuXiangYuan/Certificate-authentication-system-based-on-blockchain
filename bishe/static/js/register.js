$(function(){
    $(".institution").eq($(this).val()).hide();
});

function showInstitution(val){
    console.log(val);
    if("1" == val) {
        institution.style.display = "none";
        insError.style.display="none";
    }
    else
        institution.style.display="block";
}

function check_name(){
    var name = document.getElementById("name").value;
    nameError.style.display="block";
    if(name == '')
        document.getElementById("nameError").innerHTML="<font color='red'>姓名不能为空</font>";
    else if(name.length < 2)
        document.getElementById("nameError").innerHTML="<font color='red'>请输入正确的姓名</font>";
    else
        nameError.style.display="none";
}

function check_phone(){
    var reg =/^0?1[3|4|5|6|7|8][0-9]\d{8}$/;
    var phone = document.getElementById("phone").value;
    phoneError.style.display="block";
    if(phone == '')
        document.getElementById("phoneError").innerHTML="<font color='red'>手机号不能为空</font>";
    else if(!reg.test(phone))
        document.getElementById("phoneError").innerHTML="<font color='red'>请输入正确的手机号</font>";
    else
        phoneError.style.display="none";
}

function check_email(){
    var email = document.getElementById("email").value;
    var reg = /^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$/;
    emailError.style.display="block";
    if(email == '')
        document.getElementById("emailError").innerHTML="<font color='red'>邮箱不能为空</font>";
    else if(!reg.test(email))
        document.getElementById("emailError").innerHTML="<font color='red'>邮箱格式不正确</font>";
    else
        emailError.style.display="none";
}

function check_pw1(){
    var pw1 = document.getElementById("password").value;
    pwerror.style.display="block";
    if(pw1 === ''){
        document.getElementById("pwerror").innerHTML="<font color='red'>密码不能为空</font>";
    }
    else if(pw1.length < 10){
        document.getElementById("pwerror").innerHTML="<font color='red'>密码不能小于10位</font>";
    }
    else
        pwerror.style.display="none";
}

function check_pw2(){
    var pw1 = document.getElementById("password").value;
    var pw2 = document.getElementById("password2").value;
    pw2error.style.display="block";
    if(pw1 == pw2){
        pw2error.style.display="none";
    }
    else
        document.getElementById("pw2error").innerHTML="<font color='red'>两次密码输入不一样</font>";
}

function check_ins(){
    var ins = document.getElementById("institution_name").value;
    insError.style.display="block";
    if(ins == '')
        document.getElementById("insError").innerHTML="<font color='red'>校名/机构名不能为空</font>";
    else
        insError.style.display="none";
}
