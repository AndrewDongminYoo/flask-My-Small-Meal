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

async function getFoods(lat, long) {
    const response = await fetch(`/api/shop?lat=${lat}&lng=${long}`);
    return await response.json()
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
            let categories = []
            restaurants.forEach((restaurant, index) => {
                categories.push(...restaurant['categories'])
                let i = index % 3
                showCards(restaurant, i)
            }) // tempHtml append 하기
            let unique = new Set(categories)
            categories = [...unique]
            console.log(categories)
        })  // like 여부에 따라 html 달리 할 필요가 있을까..?
    }
    function error(e) {
        console.error(e)
    }
}

const userCheck = () => {
    user = localStorage.getItem("delivery-uuid")
    if (user === null) {
        user = uuidv4()
        localStorage.setItem("delivery-uuid", user)
        console.log(user)
    }
    showBookmarks(user);
}

function keep(id) {
    event.target.classList.add('is-hidden')
    const headers = new Headers();
    headers.append('content-type', 'application/json')
    const body = JSON.stringify({uuid: user, ssid: id, action: 'like'});
    const init = {method: 'POST', headers, body};
    fetch(`/api/like`, init)
        .then((r) => r.headers.get('content-type').includes('json') ? r.json() : r.text())
        .then((r) => console.log(r))
        .catch((e) => console.log(e));
    event.target.nextElementSibling.classList.remove('is-hidden')
} // 특정 상점 좋아요하기

function remove(id) {
    event.target.classList.add('is-hidden')
    const headers = new Headers();
    headers.append('content-type', 'application/json')
    const body = JSON.stringify({uuid: user, ssid: id, action: 'dislike'});
    const init = {method: 'POST', headers, body};
    fetch(`/api/like`, init)
        .then((r) => r.headers.get('content-type').includes('json') ? r.json() : r.text())
        .then((r) => console.log(r))
        .catch((e) => console.log(e));
    event.target.previousElementSibling.classList.remove('is-hidden')
} // 특정 상점 좋아요 취소하기

function showBookmarks(user) {
    fetch(`/api/like?uuid=${user}`)
        .then((r) => r.headers.get('content-type').includes('json') ? r.json() : r.text())
        .then((r) => console.log(r['restaurants']))
        .catch((e) => console.log(e));
} // 모든 즐겨찾기 상품 조회하기

const showCards = (restaurant, i) => {
    let {id, name, reviews, owner, categories, image, logo, address, rating, time, min_order} = restaurant;
    if (!image) {
        return
    }
    let tempHtml = `
        <div class="food-card card">
            <div class="image-box card-image">
                <figure class="image">
                    <img class="food-image image" src="${image}"
                         alt="food-thumbnail">
                </figure>
            </div>
            <div class="tool-box">
                <div class="book-mark">
                    <div class="store_name">${name}<br>⭐${rating}점</div>
                    <button class="button book-button" onclick="keep('${id}')">⭐keep</button>
                    <button class="button book-button is-hidden" onclick="remove('${id}')">🌟delete</button>
                </div>
                
                <div class="buttons are-small" id="btns${i}">{__buttons__}</div>
                <div class="card-footer">
                    <div>${address}<br>영업시간: ${time}<br>${min_order}원 이상 주문 가능</div>
                    <div class="reviews">
                        <div class="reviews-count">주문자리뷰 ${reviews}<br>사장님댓글 ${owner}</div>
                    </div>
                </div>
            </div>
        </div>`
    let btn = ""
    categories.forEach((tag)=>{
        btn += `<button class="button is-rounded is-warning is-outlined" onclick="highlight('${tag}')">#${tag}</button>`
    })
    $(`.column-${i}`).append(tempHtml.replace("{__buttons__}", btn))
}

function search() {
    let query = $("#geoSearch").val()
    const headers = new Headers();
    headers.append('content-type', 'application/json')
    const body = JSON.stringify({query: query});
    const init = {method: 'POST', headers, body};
    fetch(`/api/address`, init)
        .then((r) => r.headers.get('content-type').includes('json') ? r.json() : r.text())
        .then((result) => {
            let long = Number(result['long']).toFixed(7)
            let lat = Number(result['lat']).toFixed(7)
            return getFoods(lat, long)
        }).then(restaurants => {
            $(".column-0").empty()
            $(".column-1").empty()
            $(".column-2").empty()
            restaurants.forEach((restaurant, index) => {
                let i = index % 3
                showCards(restaurant, i)
            }) // tempHtml append 하기
        }).catch((e) => console.log(e));
}

function highlight(string) {
    $("button.is-warning").not(`:contains(${string})`).addClass('is-outlined')
    $(`button.button:contains(${string})`).removeClass('is-outlined')
}