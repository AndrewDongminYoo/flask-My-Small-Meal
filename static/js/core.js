let user = null;
let latitude = 37.5559598;
let longitude = 126.1699723;
let isMobile = false;
let Screen = "Full Wide"
let columnCount = 3
// 유저의 값을 글로벌하게 사용하기 위해 초기화한다.
// 위도와 경도를 서울역을 기준으로 초기화한다. (사용자 접속 시 사용자의 위치로 이동)

headers = {
    accept: "*/*",
    "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "sec-ch-ua": "\"Chromium\";v=\"94\", \"Google Chrome\";v=\"94\", \";Not A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}

function geoRefresh() {
    emptyCards(); // 카드 컬럼 비우기
    geoFindMe(); // 사용자의 위치 다시 받아내기
    userCheck(); // 사용자가 처음 접속한 사람인지 확인
}

function widthCheck() {
    let width = window.innerWidth
    if (width > 1600) {
        Screen = "Full Wide"
        columnCount = 3
    } else if (width >= 1024) {
        Screen = "Wide width"
        columnCount = 3
        document.querySelector("div.column:first-child").remove()
        document.querySelector("div.column:last-child").remove()
    } else if (width > 630) {
        Screen = "Medium width"
        columnCount = 2
        document.querySelector("div.column:first-child").remove()
        document.querySelector("div.column:last-child").remove()
    } else {
        Screen = "Mobile width"
        columnCount = 1
        document.querySelector("div.column:first-child").remove()
        document.querySelector("div.column:last-child").remove()
        document.querySelector("div.column:last-child").remove()
        document.querySelector("div.column:last-child").remove()
    }
    console.log(Screen)
}

function deviceCheck() {
    const pc = "win16|win32|win64|mac|macintel";
    const this_device = navigator.platform;
    if (this_device) {
        isMobile = pc.indexOf(navigator.platform.toLowerCase()) < 0;
    }
    console.log(isMobile ? "It's on mobile" : "It's Computer")
}

function memberValidCheck() {
    if (Screen === "Mobile width") return;
    let token = getOneCookie("mySmallMealToken")
    fetch(`/api/valid?token=${token}`)
        .then((res) => res.json())
        .then((data) => {
            const {nickname, result} = data
            if (result === 'success') {
                document.querySelector(".login-btn").textContent = '로그아웃'
                document.querySelector("#bookmark-title").textContent = `${nickname}'s PICK!`
            } else {
                // 로그인이 안되면 에러메시지를 띄웁니다.
                document.querySelector(".login-btn").textContent = '로그인'
                window.alert('로그인이 필요합니다.')
                window.location.href = '/login'
                removeCookie("mySmallMealToken")
            }
        })
}

const error = () => NoGeoDontWorry();
const removeCookie = (name) => document.cookie = `${name}=; expires=Fri, 12 Aug 1994 00:00:00 GMT`;
const CheckCookies = () => document.cookie.split("; ")
const getOneCookie = (name) => CheckCookies()?.find(r => r.startsWith(name))?.split("=")[1];

async function weather() {
    if (Screen === "Mobile width") return;
    if (Screen === "Medium width") return;
    const weatherBox = document.getElementById("weather-box")
    weatherBox.innerHTML = `
        <div class="weather-title">현재날씨</div>
        <table class="table is-narrow bm-current-table" style="margin: auto;">
        <thead><tr><th>온도</th><th>습도</th><th>풍속</th><th colspan="2">날씨</th></tr></thead></table>
        `;
    let apikey = "fa5d5576f3d1c8248d37938b4a3b216b"
    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${apikey}&units=metric`;
    const response = await fetch(url).then((res) => res.json()).catch()
    const {weather, wind} = await response;
    const {humidity, temp} = await response['main'];
    const {description, main, icon} = await weather[0];
    document.querySelector(".bm-current-table").innerHTML += `
        <tbody><tr>
        <td>${temp}&#8451;</td>
        <td>${humidity}&#37;</td>
        <td>${wind.speed}m/s</td>
        <td>${main}</td>
        <td><img src="https://openweathermap.org/img/w/${icon}.png" alt="${description}"></td>
        </tr></tbody>`;
}

// 위도 경도에 따라 주변 맛집을 받아오는 내부 api 송출
async function getFoods(lat, long) {
    if (!(lat && long)) {
        const response = await fetch(`/api/shop?lat=${latitude}&lng=${longitude}`);
        return await response.json()
    } else {
        const response = await fetch(`/api/shop?lat=${lat}&lng=${long}`);
        return await response.json()
    }
}

// geoLocation api 이용한 현재 사용자의 위치 받아내는 코드
function geoFindMe() {
    if (!navigator.geolocation) {
        console.log('Geolocation is not supported by your browser');
    } else {
        navigator.geolocation.getCurrentPosition(success, error);
    }
}

//위치 받아내기 성공했을 때의 메소드
function success(position) {
    latitude = position.coords.latitude;
    longitude = position.coords.longitude;
    // weather(latitude,longitude)
    let start = Date.now()
    getFoods(latitude, longitude)
        .then(restaurants => {
            emptyCards()
            let categories = []
            restaurants.forEach((restaurant, index) => {
                categories.push(...restaurant['categories'])
                let i = index % columnCount
                showCards(restaurant, i)
            }) // tempHtml append 하기
            let end = Date.now()
            console.log(`It Takes ${(end - start) / 1000} seconds....`)
            if (getOneCookie('roulette')) return;
            if (Screen === "Mobile width") return;
            let unique = new Set(categories)
            categories = [...unique]
            modal()
            categories = categories.filter((v) => v !== '1인분주문')
            shuffle(categories)
            let tempHTML = "<span>[</span>";
            categories.forEach((word, i) => {
                tempHTML += `<span title="${word}" class="word word-${i}">${word}, </span>`;
            })
            tempHTML += "<span>]</span>";
            document.querySelector(".modal-content").innerHTML = tempHTML;
            everybodyShuffleIt(categories).then((result) => result && console.log(`오늘은 ${result} 먹자!!`))
        })  // like 여부에 따라 html 달리 할 필요가 있을까..?
}

async function NoGeoDontWorry() {
    const response = await fetch(`/api/shop?lat=${latitude.toFixed(7)}&lng=${longitude.toFixed(7)}`);
    let restaurants = await response.json()
    emptyCards()
    restaurants.forEach((restaurant, index) => {
        let i = index % columnCount
        showCards(restaurant, i)
    }) // tempHtml append 하기
}

// 모달 + 모달 닫기 위한 닫기 버튼과 어두운 배경 나타내기

function modal() {
    // if (isMobile) return;
    document.getElementById("modal").classList.add("is-active")
    document.getElementById("modal").style.display = 'grid';
    document.getElementById("modal").style['place-items'] = 'center';
}

// 로컬 스토리지에 사용자의 uuid 가 있는지 확인하고 없으면 새로 발급한다.
function userCheck() {
    user = localStorage.getItem("delivery-uuid")
    if (user === null) {
        user = uuidv4()
        localStorage.setItem("delivery-uuid", user)
    }
    console.log(`user: ${user}`);
    // 받은 사용자의 uuid 를 조회해 2초 후에 화면에 즐겨찾기 리스트를 띄운다.
    setTimeout(() => showBookmarks(user), 2000)
}

// 특정 식당을 즐겨찾기 하는 코드
function keep(_id, min_order) {
    changeBtn(_id, false)
    const headers = new Headers();
    headers.append('content-type', 'application/json')
    const body = JSON.stringify({uuid: user, _id, min_order, action: 'like', mode: "cors"});
    sendLike(user, headers, body)
}

// 특정 식당을 즐겨찾기 삭제하는 코드
function remove(_id, min_order) {
    changeBtn(_id, true)
    const headers = new Headers();
    headers.append('content-type', 'application/json')
    const body = JSON.stringify({uuid: user, _id, min_order, action: 'dislike', mode: "cors"});
    sendLike(user, headers, body)
}

// remove 코드의 메인 부분만을 추출한 코드 (북마크 탭에서 직접 삭제 다루기 위해 분리)
function delMark(_id, min_order) {
    changeBtn(_id, true)
    const body = JSON.stringify({uuid: user, _id, min_order, action: 'dislike', mode: "cors"});
    sendLike(user, headers, body)
}

function changeBtn(_id, afterDelete) {
    if (afterDelete) {
        document.querySelector(`.delete-${_id}`).classList.add("is-hidden")
        document.querySelector(`.keep-${_id}`).classList.remove("is-hidden")
    } else {
        document.querySelector(`.keep-${_id}`).classList.add("is-hidden")
        document.querySelector(`.delete-${_id}`).classList.remove("is-hidden")
    }
}

// 즐겨찾기에 등록 or 해제 하는 코드의 공통 코드 추출
function sendLike(user, headers, body) {
    const init = {method: 'POST', headers, body};
    fetch(`/api/like`, init)
        .then((r) => r.headers.get('content-type').includes('json') ? r.json() : r.text())
        .then(() => {
            showBookmarks(user);
        })
        .catch((e) => console.log(e));
}

// 즐겨찾기 목록을 불러오는 코드 ("즐겨찾기목록")이라는 헤더도 이 때 보여줌.
function showBookmarks(user) {
    if (Screen === "Mobile width") return;
    let ex = document.querySelector("#aside");
    console.log(ex);
    document.querySelector("#aside").style.display = "block"
    fetch(`/api/like?uuid=${user}`)
        .then((r) => r.headers.get('content-type').includes('json') ? r.json() : r.text())
        .then((res) => {
            document.getElementById("bookmarks").innerHTML = "";
            res['restaurants'] && res['restaurants'].forEach((r) => bookMark(r)); // 북마크 배열이 '도착하면' 렌더링
        })
        .catch((e) => console.log(e));
    document.getElementById("aside").classList.add("open");
}

// 즐겨찾기 목록에 북마크 내용들을 담아 넣는 코드
const bookMark = (restaurant) => {
    let {_id, name, phone, time, min_order} = restaurant;
    let tempHtml = `
        <li class="bookmark is-hoverable panel-block" title="전화번호: ${phone} / 영업시간: ${time}" id="pop-${_id}" onclick="popUp(${_id})">
        <span class="mark-menu">${name}</span>
        <button class="button is-xs is-inline-block" onclick="delMark(${_id}, ${min_order})" onmouseover="">⨉</button></li>`
    document.getElementById("bookmarks").innerHTML += tempHtml;
}

let lowModalBody = document.getElementById('low-modal-body');

// 즐겨찾기 클릭시 모달창 오픈
function popUp(_id) {
    fetch(`/api/detail?_id=${_id}`).then((restaurant) => {
        let {image, name, address, time, min_order, phone, categories} = restaurant;
        let tempHtml = `
            <div class="pop-up-card">
                <button class="button close-button" onclick="lowModalBody.style.display='none';">⨉</button>
                <div class="pop-card-head">
                    <img class="pop-card-head-image" src="${image}" alt="${name}">
                </div>
                <div class="pop-card-content-1">
                    <div class="pop-card-store-name">"${name}"</div>
                    <div class="pop-card-hash">{__buttons__}</div>
                </div>
                <div class="pop-card-content-2">
                    <div class="pop-card-address">${address ? address : "주소가 정확하지 않습니다."}</div>
                    <div class="pop-card-schedule">영업시간: ${time ? time : "영업시간 정보가 없습니다."}</div>
                    <div class="pop-card-min">${min_order ? min_order : "---"} 원 이상 주문가능</div>
                    <div class="pop-card-phone-number">${phone ? phone : "전화번호가 없습니다."}</div>
                </div>
            </div>`
        let btn = ""
        categories.forEach((tag) => btn += `<span>#${tag}</span>`)
        lowModalBody.style.display = "block";
        lowModalBody.innnerHTML = tempHtml.replace("{__buttons__}", btn)
        // 각 카드의 카테고리 해시태그를 replace 하는 가상 template 코드
        // 특정 즐겨찾기 메뉴 클릭시 팝업창이 띄어짐과 동시에 해당 즐겨찾기 메뉴가 흰색으로 바뀐다.
    })
}

function emptyCards() {
    document.querySelector(".column-0").innerHTML = ""
    if (Screen === "Mobile width") return;
    document.querySelector(".column-1").innerHTML = ""
    if (Screen === "Medium width") return;
    document.querySelector(".column-2").innerHTML = ""
}

// URl 끝의 # 값이 변하면 그에 맞게 새롭게 리스트를 받아옵니다 (sort 바꿔줌)
window.addEventListener('hashchange', async () => {
    let hash = window.location.hash.substring(1)
    const response = await fetch(`/api/shop?order=${hash}&lat=${latitude}&lng=${longitude}`);
    let restaurants = await response.json()
    emptyCards()
    restaurants.forEach((restaurant, index) => {
        let i = index % 3
        showCards(restaurant, i)
    })
})

// 레스토랑 하나하나의 카드를 만들어내는 코드
const showCards = (restaurant, i) => {
    let {
        _id, name, reviews,
        owner, categories,
        image, address,
        rating, time,
        min_order, phone
    } = restaurant;
    // 이미지가 없는 경우 VIEW 가 좋지 않아 리턴시킨다.
    if (!image) return;
    let tempHtml = `
    <div class="food-card card">
        <div class="image-box card-image">
            <figure class="image" title="${phone}">
                <img class="food-image image" src="${image}"
                     alt="${name}-food-thumbnail">
            </figure>
        </div>
        <div class="tool-box">
            <div class="book-mark">
                <div class="store_name">${name}<br>⭐${rating}점</div>
                <button class="button book-button keep-${_id}" onclick="keep(${_id}, ${min_order})">⭐keep</button>
                <button class="button book-button is-hidden delete-${_id}" onclick="remove(${_id}, ${min_order})">🌟delete</button>
            </div>
            <div class="buttons are-small btns">{__buttons__}</div>
            <div class="card-footer">
                <div>${address}<br>영업시간: ${time}<br>${min_order}원 이상 주문 가능</div>
                <div class="reviews">
                    <div class="reviews-count">주문자리뷰 ${reviews}<br>사장님댓글 ${owner}</div>
                </div>
            </div>
        </div>
    </div>`
    let btn = ""
    // 각 카드의 카테고리 해시태그를 replace 하는 가상 template 코드
    categories.forEach((tag) => {
        btn += `<button value="${tag}" class="button is-rounded is-warning is-outlined" onclick="highlight('${tag}')">#${tag}</button>`
    })
    document.querySelector(`.column-${i.toString()}`).innerHTML += tempHtml.replace("{__buttons__}", btn)
}

// 직접적으로 주소를 입력해서 배달 음식점을 찾고자 할 때 쓰입니다.
function search() {
    let query = document.querySelector("#geoSearch").value
    const body = JSON.stringify({query, mode: "cors"});
    const init = {method: 'POST', body};
    console.log(init)
    fetch(`/api/address`, init)
        .then((r) => r.headers.get('content-type').includes('json') ? r.json() : r.text())
        .then((result) => {
            if (result['long'] && result['lat']) {
                longitude = Number(result['long']).toFixed(7)
                latitude = Number(result['lat']).toFixed(7)
            }
            return getFoods(latitude, longitude)
        }).then(restaurants => {
        emptyCards()
        restaurants.forEach((restaurant, index) => {
            let i = index % 3
            showCards(restaurant, i)
        }) // tempHtml append 하기
    }).catch((e) => console.log(e));
}

// 특정 카테고리 (예: 1인분주문) 를 클릭하면 모든 식당 중 해당 해시태그를 가진 카드가 하이라이트됩니다.
function highlight(string) {
    document.querySelectorAll(`button.is-warning:not([value='${string}'])`).forEach(e => e.classList.add('is-outlined'))
    document.querySelectorAll(`button.button[value='${string}']`).forEach(e => e.classList.remove('is-outlined'))
}

// tab 의 버튼을 클릭하면 그 버튼만 active 상태가 됩니다.
function tabFocus(string) {
    document.querySelectorAll(`li.tab:not(.tab-${string})`).forEach(e => e.classList.remove('is-active'));
    document.querySelector(`li.tab-${string}`).classList.add('is-active');
}

// 비동기처리 방식 자바스크립트를 고려한 타이머 함수
const timer = ms => new Promise(r => setTimeout(r, ms))

// 리스트의 순서를 뒤섞는 함수입니다.
function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array
}

// 모달에 띄운 화면 속 텍스트가 번갈아가면서 빨간색으로 변하다가 멈추고 결과 출력
async function everybodyShuffleIt(array) {
    const result = shuffle(array)[0]
    for (let i = 0; i < array.length; i++) {
        await timer(60)
        document.querySelectorAll(`span.word:not(.word-${i})`).forEach(e => e.classList.remove('is-red'));
        document.querySelector(`span.word.word-${i}`)?.classList.add('is-red')
    }
    for (let i = 0; i < array.length; i++) {
        await timer(100)
        document.querySelectorAll(`span.word:not(.word-${i})`).forEach(e => e.classList.remove('is-red'));
        document.querySelector(`span.word.word-${i}`)?.classList.add('is-red')
    }
    for (let i = 0; i < array.length; i++) {
        await timer(200)
        document.querySelectorAll(`span.word:not(.word-${i})`).forEach(e => e.classList.remove('is-red'));
        document.querySelector(`span.word.word-${i}`)?.classList.add('is-red')
    }
    for (let i = 0; i < array.length; i++) {
        await timer(600)
        document.querySelectorAll(`span.word:not(.word-${i})`).forEach(e => e.classList.remove('is-red'));
        document.querySelector(`span.word.word-${i}`)?.classList.add('is-red')
        if (document.querySelector(`.word-${i}`)?.classList.contains('is-red') && document.querySelector(`.word-${i}`)['title'] === result) {
            document.querySelector(`button.button[value='${result}']`).classList.remove('is-outlined')
            await timer(100)
            alert(`오오~~ 오늘은 ${result} 먹으면 되겠다!!!!`)
            document.getElementById("modal").remove()
            return result
        }
        document.cookie = "roulette=true;";
    }
}

