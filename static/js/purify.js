let user = null, latitude = 37.5559598, longitude = 126.1699723;

async function weather() {
  const t = $("#weather-box");
  t.empty(), t.append(' <div class="weather-title">현재날씨</div> <table class="table is-narrow bm-current-table" style="margin: auto;"> <thead><tr><th>온도</th><th>습도</th><th>풍속</th><th>날씨</th><th>아이콘</th></tr></thead></table> '), await t.append(' <div class="weather-title">4일 동안의 일일 예보</div> <table class="table is-narrow bm-daily-table" style="margin: auto;"><thead><tr> <th>아침온도</th><th>낮온도</th><th>저녁온도</th><th>밤온도</th><th>습도</th><th>아이콘</th> </tr></thead></table> ');
  const e = "https://api.openweathermap.org/data/2.5/onecall?lat=" + latitude.toFixed(7) + "&lon=" + longitude.toFixed(7) + "&appid=fa5d5576f3d1c8248d37938b4a3b216b&lang=kr&units=metric",
    n = await fetch(e).then(t => t.json()).catch(), { current: o, daily: a } = await n, {
      feels_like: s,
      humidity: i,
      weather: d,
      wind_speed: r
    } = await o, { description: l, icon: c } = await d[0];
  a.length = 4, $(".bm-current-table").append(` <tbody><tr> <td>${Math.floor(s)} ℃</td> <td>${i} %</td> <td>${r} m/s</td> <td>${l}</td> <td><img src="http://openweathermap.org/img/w/${c}.png" alt="${l}"></td> </tr></tbody> `), await a.forEach(t => {
    const { feels_like: e, humidity: n, weather: o } = t, { day: a, night: s, eve: i, morn: d } = e, {
      description: r,
      icon: l
    } = o[0];
    $(".bm-daily-table").append(` <tbody><tr> <td>${d.toFixed(1)} ℃</td> <td>${a.toFixed(1)} ℃</td> <td>${i.toFixed(1)} ℃</td> <td>${s.toFixed(1)} ℃</td> <td>${n} %</td> <td><img src="http://openweathermap.org/img/w/${l}.png" title="${r}" alt="${r}"></td> </tr></tbody> `)
  })
}

function geoRefresh() {
  $(".column-0").empty(), $(".column-1").empty(), $(".column-2").empty(), geoFindMe(), userCheck()
}

async function getFoods(t, e) {
  if (t && e) {
    const n = await fetch(`/api/shop?lat=${t}&lng=${e}`);
    return await n.json()
  }
  {
    const t = await fetch(`/api/shop?lat=${latitude.toFixed(7)}&lng=${longitude.toFixed(7)}`);
    return await t.json()
  }
}

function geoFindMe() {
  navigator.geolocation ? navigator.geolocation.getCurrentPosition(success, error) : console.log("Geolocation is not supported by your browser")
}

function success(t) {
  latitude = t.coords.latitude, longitude = t.coords.longitude, getFoods(latitude, longitude).then(t => {
    let e = [];
    t.forEach((t, n) => {
      e.push(...t.categories), showCards(t, n % 3)
    });
    let n = new Set(e);
    e = [...n], modal(), shuffle(e = e.filter(t => "1인분주문" !== t));
    let o = "<span>[</span>";
    e.forEach((t, e) => {
      o += `<span class="word word-${e}">${t}, </span>`
    }), o += "<span>]</span>", document.querySelector(".modal-content").innerHTML = o, everybodyShuffleIt(e).then(t => t && console.log(`오늘은 ${t} 먹자!!`)), document.querySelector("#modal").classList.remove("is-active")
  })
}

window.onload = function () {
  geoFindMe(), userCheck(), weather().then()
};
const error = () => NoGeoDontWorry();

async function NoGeoDontWorry() {
  const t = await fetch(`/api/shop?lat=${latitude.toFixed(7)}&lng=${longitude.toFixed(7)}`);
  let e = await t.json();
  $(".column-0").empty(), $(".column-1").empty(), $(".column-2").empty(), e.forEach((t, e) => {
    showCards(t, e % 3)
  })
}

function modal() {
  $("#modal").addClass("is-active")
}

const userCheck = () => {
  null === (user = localStorage.getItem("delivery-uuid")) && (user = uuidv4(), localStorage.setItem("delivery-uuid", user)), setTimeout(() => showBookmarks(user), 2e3)
};

function keep(t, e) {
  changeBtn(t, !1);
  const n = new Headers;
  n.append("content-type", "application/json");
  const o = JSON.stringify({ uuid: user, ssid: t, min_order: e, action: "like" });
  sendLike(user, n, o)
}

function remove(t) {
  changeBtn(t, !0);
  const e = new Headers;
  e.append("content-type", "application/json");
  const n = JSON.stringify({ uuid: user, ssid: t, action: "dislike" });
  sendLike(user, e, n)
}

function delMark(t) {
  changeBtn(t, !0);
  const e = new Headers;
  e.append("content-type", "application/json");
  const n = JSON.stringify({ uuid: user, ssid: t, action: "dislike" });
  sendLike(user, e, n)
}

function changeBtn(t, e) {
  e ? ($(`#delete-${t}`).addClass("is-hidden"), $(`#keep-${t}`).removeClass("is-hidden")) : ($(`#keep-${t}`).addClass("is-hidden"), $(`#delete-${t}`).removeClass("is-hidden"))
}

function sendLike(t, e, n) {
  fetch("/api/like", {
    method: "POST",
    headers: e,
    body: n
  }).then(t => t.headers.get("content-type").includes("json") ? t.json() : t.text()).then(() => {
    showBookmarks(t)
  }).catch(t => console.log(t))
}

function showBookmarks(t) {
  $("h2.h2").show(), fetch(`/api/like?uuid=${t}`).then(t => t.headers.get("content-type").includes("json") ? t.json() : t.text()).then(t => {
    $("#bookmarks").empty(), t.restaurants.forEach(t => bookMark(t))
  }).catch(t => console.log(t)), $("#aside").addClass("open")
}

const bookMark = t => {
  let { ssid: e, name: n, phone: o, time: a } = t,
    s = ` <li class="bookmark is-hoverable panel-block" title="전화번호: ${o} / 영업시간: ${a}" id="pop-${e}" onclick="popUp('${e}')"> <span class="mark-menu">${n}</span> <button class="button is-xs is-inline-block" onclick="delMark('${e}')" onmouseover="">⨉</button></li>`;
  $("#bookmarks").append(s)
};

function popUp(t) {
  $.ajax({
    url: `/api/detail?ssid=${t}`, type: "GET", data: {}, success: function (t) {
      let { ssid: e, image: n, name: o, address: a, time: s, min_order: i, phone: d, categories: r } = t,
        l = ` <div class="pop-up-card"> <button class="button close-button" onclick="$('#low-modal-body').hide();">⨉</button> <div class="pop-card-head"> <img class="pop-card-head-image" src="${n}" alt="${o}"> </div> <div class="pop-card-content-1"> <div class="pop-card-store-name">"${o}"</div> <div class="pop-card-hash">{__buttons__}</div> </div> <div class="pop-card-content-2"> <div class="pop-card-address">${a || "주소가 정확하지 않습니다."}</div> <div class="pop-card-schedule">영업시간: ${s || "영업시간 정보가 없습니다."}</div> <div class="pop-card-min">${i || "---"} 원 이상 주문가능</div> <div class="pop-card-phone-number">${d || "전화번호가 없습니다."}</div> </div> </div>`,
        c = "";
      r.forEach(t => {
        c += `<span>#${t}</span>`
      });
      let u = $("#low-modal-body");
      $(`#pop-${e}`);
      u.show(), u.html(l.replace("{__buttons__}", c))
    }
  })
}

window.addEventListener("hashchange", async () => {
  let t = window.location.hash.substring(1);
  const e = await fetch(`/api/shop?order=${t}&lat=${latitude}&lng=${longitude}`);
  let n = await e.json();
  $(".column-0").empty(), $(".column-1").empty(), $(".column-2").empty(), n.forEach((t, e) => {
    showCards(t, e % 3)
  })
});
const showCards = (t, e) => {
  let {
    id: n,
    name: o,
    reviews: a,
    owner: s,
    categories: i,
    image: d,
    address: r,
    rating: l,
    time: c,
    min_order: u
  } = t;
  if (!d) return;
  let h = ` <div class="food-card card"> <div class="image-box card-image"> <figure class="image" title="${c}"> <img class="food-image image" src="${d}" alt="${o}-food-thumbnail"> </figure> </div> <div class="tool-box"> <div class="book-mark"> <div class="store_name">${o}<br>⭐${l}점</div> <button class="button book-button" id="keep-${n}" onclick="keep('${n}', '${u}')">⭐keep</button> <button class="button book-button is-hidden" id="delete-${n}" onclick="remove('${n}')">🌟delete</button> </div> <div class="buttons are-small" id="btns${e}">{__buttons__}</div> <div class="card-footer"> <div>${r}<br>영업시간: ${c}<br>${u}원 이상 주문 가능</div> <div class="reviews"> <div class="reviews-count">주문자리뷰 ${a}<br>사장님댓글 ${s}</div> </div> </div> </div> </div>`,
    p = "";
  i.forEach(t => {
    p += `<button class="button is-rounded is-warning is-outlined" onclick="highlight('${t}')">#${t}</button>`
  }), $(`.column-${e}`).append(h.replace("{__buttons__}", p))
};

function search() {
  let t = $("#geoSearch").val();
  const e = new Headers;
  e.append("content-type", "application/json");
  const n = JSON.stringify({ query: t });
  fetch("/api/address", {
    method: "POST",
    headers: e,
    body: n
  }).then(t => t.headers.get("content-type").includes("json") ? t.json() : t.text()).then(t => (t.long && t.lat && (longitude = Number(t.long).toFixed(7), latitude = Number(t.lat).toFixed(7)), getFoods(latitude, longitude))).then(t => {
    $(".column-0").empty(), $(".column-1").empty(), $(".column-2").empty(), t.forEach((t, e) => {
      showCards(t, e % 3)
    })
  }).catch(t => console.log(t))
}

function highlight(t) {
  $("button.is-warning").not(`:contains(${t})`).addClass("is-outlined"), $(`button.button:contains(${t})`).removeClass("is-outlined")
}

function tabFocus(t) {
  $("li.tab").not(`.tab-${t}`).removeClass("is-active"), $(`li.tab-${t}`).addClass("is-active")
}

const timer = t => new Promise(e => setTimeout(e, t));

function shuffle(t) {
  for (let e = t.length - 1; e > 0; e--) {
    let n = Math.floor(Math.random() * (e + 1));
    [t[e], t[n]] = [t[n], t[e]]
  }
  return t
}

async function everybodyShuffleIt(t) {
  const e = shuffle(t)[0];
  for (let e = 0; e < t.length; e++) await timer(60), $(`span.word.word-${e}`).addClass("is-red"), $("span.word").not(`.word-${e}`).removeClass("is-red");
  for (let e = 0; e < t.length; e++) await timer(100), $(`span.word.word-${e}`).addClass("is-red"), $("span.word").not(`.word-${e}`).removeClass("is-red");
  for (let e = 0; e < t.length; e++) await timer(200), $(`span.word.word-${e}`).addClass("is-red"), $("span.word").not(`.word-${e}`).removeClass("is-red");
  for (let n = 0; n < t.length; n++) if (await timer(600), $("span.word").not(`.word-${n}`).removeClass("is-red"), $(`span.word.word-${n}`).addClass("is-red"), $(`span.word-${n}:contains('${e},')`).hasClass("is-red")) return $(`button.button:contains(${e})`).removeClass("is-outlined"), await timer(100), alert(`오오~~ 오늘은 ${e} 먹으면 되겠다!!!!`), $("div").remove("#modal"), $("#modal").remove(), e
}