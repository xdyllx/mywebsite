function goToTopic(topic) {
    var topics = ["design", "sports", "music", "entertainment", "dev"];
    if (topics.indexOf(topic) === -1) { return false; }

    removeActive();
    $("#intro").removeClass("active");
    $("#" + topic).addClass("active");
    $("#" + topic + "-bg").addClass("active");
    $("#" + topic + "-descr").addClass("active");
    $(".content").addClass("active " + topic);
}

function goToMaster() {
    removeActive();
    $("#intro").addClass("active");
    $("#master").addClass("active");
}

function removeActive() {
    $(".tile-container").removeClass("active");
    $(".background").removeClass("active");
    $(".descr-box").removeClass("active");
    $(".content").removeClass("design sports music entertainment dev");
}

$(function() {
    $("a[href='#master']").click(function(e) {
        e.preventDefault();
        goToMaster();
    });

    $.each(["design", "sports", "music", "entertainment", "dev"], function() {
        var that = this;
        $("a[href='#" + this + "']").click(function(e) {
            e.preventDefault();
            goToTopic(that.toString());
        });
    });
});
