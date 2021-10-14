function loginApi() {
    $.ajax({
        type: "POST",
        url: "/api/login",
        data: {email: $('#member-email').val(), pw: $('#member-pw').val()},
        success: function (response) {
            if (response['result'] === 'success') {
                // 로그인이 정상적으로 되면, 토큰을 받아옵니다.
                // 이 토큰을 mytoken 이라는 키 값으로 쿠키에 저장합니다.
                $.cookie('mytoken', response['token']);

                alert('로그인 완료!')
                window.location.href = '/'
            } else {
                // 로그인이 안되면 에러메시지를 띄웁니다.
                alert(response['msg'])
            }
        }
    })
}

function kakaoLoginApi(env) {
    let redirect_uri = ''
    if (env === 'development') {
        redirect_uri = 'http://localhost:5000/kakaoCallback'
    } else {
        redirect_uri = 'https://mysmallmeal.shop:8000/kakaoCallback'
    }

    window.location.href = `https://kauth.kakao.com/oauth/authorize?client_id=b702be3ada9cbd8f018e7545d0eb4a8d&redirect_uri=${redirect_uri}&response_type=code`
}

function registerPage() {
    window.location.href = "/register"
}

function loginPage() {
    window.location.href = '/login'
}

function registerApi() {
    const email = $('#user-email').val()
    const pw = $('#user-pw').val()
    const pwre = $('#user-pw-re').val()
    const nickname = $('#user-nick').val()
    console.log(email, pw, pwre, nickname)
    const regExp = /^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$/i;
    if (email.match(regExp) == null) {
        alert('이메일형식에 맞지 않습니다.')
        return;
    }
    if (pw.length <= 0) {
        alert('비밀번호를 입력해주세요.')
        return;
    }
    if (pw != pwre) {
        alert('비밀번호가 일치하지 않습니다.')
        return;
    }
    if (nickname.length <= 0) {
        alert('별명을 입력해주세요.')
        return;
    }


    $.ajax({
        type: "POST",
        url: "/api/register",
        data: {
            email: email,
            pw: pw,
            nickname: nickname
        },
        success: function (response) {
            console.log(response)
            if (response['result'] == 'success') {
                alert('회원가입이 완료되었습니다.')

                window.location.href = '/login'
            } else {
                alert(response['msg'])
            }
        }
    })


}