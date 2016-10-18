var lng = window.navigator.userLanguage || window.navigator.language;
moment.locale(lng);

function startStopWatch(stopwatchId, expirationDate) {
    var view = document.getElementById(stopwatchId);

    function update() {
        view.textContent = moment.duration(moment(expirationDate) - moment()).humanize(true);
    }

    update();
    setInterval(update, 1000);
}