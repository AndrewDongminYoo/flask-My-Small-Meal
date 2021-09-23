window.onload = function(){
    geoFindMe();
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
        getFoods(latitude, longitude).then(r => {
            console.log(r)
        })
    }

    function error(e) {
        console.error(e)
    }

    async function getFoods(latitude, longitude) {
        const response = await fetch(`/api/shop?lat=${latitude}&lng=${longitude}`);
        return await response.json()
    }
}
