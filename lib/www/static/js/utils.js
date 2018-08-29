'use strict';

var base_url = window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + "/";

function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};


function callback_nothing(res) {}


function show_ws_error(str) {
    $("#ws-error-box .ws-error-text").text(str);
    $("#ws-error-box").show("drop", {"direction": "down"}, 300);
    setTimeout(function() {
        $("#ws-error-box").hide("drop", {"direction": "down"}, 300);
        return 0;
    }, 4000);
}

function show_ws_info(str) {
    $("#ws-info-box .ws-info-text").text(str);
    $("#ws-info-box").show("drop", {"direction": "down"}, 300);
    setTimeout(function() {
        $("#ws-info-box").hide("drop", {"direction": "down"}, 300);
        return 0;
    }, 4000);
}


function call_api(action, args, callback) {
    args["userid"] = userid;
    $.ajax({
        url: base_url + action,
        data: args,
        success: function(res) {
            if (res["status"] != 0) {
                if (res["body"] === undefined) {
                    show_ws_error(res["error"]);
                } else {
                    show_ws_error(res["body"]);
                }
                return 0;
            }

            callback(res["body"]);
            return 0;
        },
        fail: function(message) {
            show_ws_error(message);
            return 0;
        }
    });
}

function redirect_to_auth() {
    window.location.replace("https://account.withings.com/connectionuser/account_login?boring=f&redirectisfutile=t&r=https%3A%2F%2Fayaa.corp.withings.com%2F");
}


function create_user() {

    $.ajax({
        url: "https://labs.withings.com/index/service/v2/user",
        data: {
            sessionid: sessionid,
            action: "get",
            userid: userid
        },
        success: function(res) {
            if (res["status"] != 0) {
                // Fail !
                show_ws_error(JSON.stringify(res));
                return 0;
            }

            var user = res["body"];
            show_ws_info("Created player profile!");
            call_api("player_create", {
                userid: userid,
                info: JSON.stringify(user)
                }, run);

            return 0;
        },
        fail: function(message) {
            show_ws_error(message);
            return 0;
        }
    });
}
