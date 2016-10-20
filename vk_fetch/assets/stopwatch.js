var lng = window.navigator.userLanguage || window.navigator.language;
moment.locale(lng);

function startStopWatch(stopwatchId, expirationDate) {
    var view = document.getElementById(stopwatchId);

    function update() {
        var duration = moment.duration(moment(expirationDate) - moment()),
            hours = Math.trunc(duration.asHours()),
            minutes = duration.minutes();
        view.textContent = hours + ':' + minutes;
    }

    update();
    setInterval(update, 1000);
}