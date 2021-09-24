let user = null

window.onload = function () {
    geoFindMe();
    userCheck()
}

function geoRefresh() {
    $(".column-0").empty()
    $(".column-1").empty()
    $(".column-2").empty()
    geoFindMe()
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
        getFoods(latitude, longitude)
            .then(restaurants => {
                restaurants.forEach((restaurant, index) => {
                    let i = index % 3
                    showCards(restaurant, i)
                }) // tempHtml append 하기
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
    const body = JSON.stringify({ uuid: user, ssid: id.toString(), action: 'like'});
    const init = {method: 'POST', headers, body};
    fetch(`/api/like`, init)
        .then((r) => r.json())
        .then((r) => console.log(r['uuid']))
        .catch((e) => console.log(e));
} // 특정 상점 좋아요하기

function remove(id) {
    const headers = new Headers();
    headers.append('content-type', 'application/json')
    const body = JSON.stringify({ uuid: user, ssid: id.toString(), action: 'dislike'});
    const init = {method: 'POST', headers, body};
    fetch(`/api/like`, init)
        .then((r) => r.json())
        .then((r) => console.log(r['uuid']))
        .catch((e) => console.log(e));
} // 특정 상점 좋아요 취소하기

const showCards = (restaurant, i) => {
    let { id, name, reviews, owner, categories, image, logo, address, rating, time, min_order } = restaurant;
    let tempHtml = `
        <div class="food-card card">
            <div class="image-box card-image">
                <figure class="image">
                    <img class="food-image image" src="${image}"
                         alt="steak">
                </figure>
            </div>
            <div class="tool-box">
                <div class="book-mark">
                    <button class="book-button" onclick="keep('${id}')">⭐&nbsp;Save me&nbsp;</button>
                    <button class="book-button hidden" onclick="remove('${id}')">⭐&nbsp;Remove me&nbsp;</button>
                </div>
                <div class="store_name">${name}&nbsp;${time}</div>
                <div class="card-footer">
                    <div><a href="">${address}</a></div>
                    <div class="reviews">
                        <div class="reviews-count">리뷰 ${reviews} 사장님 ${owner}</div>
                    </div>
                </div>
            </div>
        </div>`
    $(`.column-${i}`).append(tempHtml)
}