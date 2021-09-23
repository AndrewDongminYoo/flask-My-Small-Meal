let user = null

window.onload = function () {
    geoFindMe();
    userCheck()
}

function geoFindMe() {
    if (!navigator.geolocation) {
        window.alert('위치 권한을 허용해 주세요!!')
        console.log('Geolocation is not supported by your browser');
    } else {
        console.log('Locating…');
        navigator.geolocation.getCurrentPosition(success, error);
    }

    function success(position) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        getFoods(latitude, longitude).then(restaurants => {
            console.log(restaurants) // tempHtml append 하기
        })  // like 여부에 따라 html 달리 할 필요가 있을까..?
    }

    function error(e) {
        console.error(e)
    }

    async function getFoods(lat, long) {
        const response = await fetch(`/api/shop?lat=${lat}&lng=${long}`);
        return await response.json()
    }
}

const userCheck = () => {
    user = localStorage.getItem("delivery-uuid")
    if (user === null) {
        user = uuidv4()
        localStorage.setItem("delivery-uuid", user)
        console.log(user)
    }
}

function keep(id) {
    const headers = new Headers();
    headers.append('content-type', 'application/json')
    const body = `{"uuid": "${user}", "ssid": "${id}", "action": "like"`;
    const init = {method: 'POST', headers, body};
    fetch(`/api/like`, init)
        .then((r) => r.json()).then((r) => console.log(r['uuid']))
        .catch((e) => console.log(e));
} // 특정 상점 좋아요하기

function remove(id) {
    const headers = new Headers();
    headers.append('content-type', 'application/json')
    const body = `{"uuid": "${user}", "ssid": "${id}", "action": "dislike"`;
    const init = {method: 'POST', headers, body};
    fetch(`/api/like`, init)
        .then((r) => console.log(r))
        .catch((e) => console.log(e));
} // 특정 상점 좋아요 취소하기