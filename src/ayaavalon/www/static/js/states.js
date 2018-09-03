'use strict';

var STATE_EMPTY = 0;
var STATE_NOT_STARTED = 1;
var STATE_WAITING_FOR_MISSION = 2;
var STATE_WAITING_FOR_VOTES = 3;
var STATE_MISSION_PENDING = 4;
var STATE_LADY = 5;
var STATE_ASSASSIN = 6;
var STATE_GAME_FINISHED = 7;

var current_state = -1;

var states_ids = {};
states_ids[STATE_EMPTY] = "content-state-empty";
states_ids[STATE_NOT_STARTED] = "content-state-not_started";
states_ids[STATE_WAITING_FOR_MISSION] = "content-state-waiting-for-mission";
states_ids[STATE_WAITING_FOR_VOTES] = "content-state-waiting-for-votes";
states_ids[STATE_MISSION_PENDING] = "content-state-mission-pending";
states_ids[STATE_LADY] = "content-state-lady";
states_ids[STATE_ASSASSIN] = "content-state-assassin";
states_ids[STATE_GAME_FINISHED] = "content-state-game-finished";

var titles = {};
titles[STATE_EMPTY] = "No Active Game";
titles[STATE_NOT_STARTED] = "Waiting for Players";
titles[STATE_WAITING_FOR_MISSION] = "Mission Proposal";
titles[STATE_WAITING_FOR_VOTES] = "Votes";
titles[STATE_MISSION_PENDING] = "Resolving Mission";
titles[STATE_LADY] = "Lady of the Lake";
titles[STATE_ASSASSIN] = "Waiting for Assassination";
titles[STATE_GAME_FINISHED] = "Game Finished!";

function update_state(game_state, animate) {
    var state = game_state["state"];

    if (state != current_state) {
        switch_state(game_state, state, animate);
        current_state = state;
    }

    generic_update(game_state);

    switch (state) {
        case STATE_EMPTY:
            update_state_empty(game_state);
            break;
        case STATE_NOT_STARTED:
            update_state_not_started(game_state);
            break;
        case STATE_WAITING_FOR_MISSION:
            update_state_waiting_for_mission(game_state);
            break;
        case STATE_WAITING_FOR_VOTES:
            update_state_waiting_for_votes(game_state);
            break;
        case STATE_MISSION_PENDING:
            update_state_mission_pending(game_state);
            break;
        case STATE_LADY:
            update_state_lady(game_state);
            break;
        case STATE_ASSASSIN:
            update_state_assassin(game_state);
            break;
        case STATE_GAME_FINISHED:
            update_state_finished(game_state);
            break;
        default:
            show_ws_error("Unknown state: " + state);
    }

    return 0;
}

function switch_state(game_state, state, animate) {
    $("#header-title").text(titles[state]);

    if (animate) {
        for (var i in states_ids) {
            $("#" + states_ids[i]).hide("drop", {"direction": "left"}, 250);
        }
        setTimeout(function() {
            $("#" + states_ids[state]).show("drop", {"direction": "right"}, 300);
        }, 300);
    } else {
        for (var i in states_ids) {
            $("#" + states_ids[i]).hide();
        }
        $("#" + states_ids[state]).show();
    }

    return 0;
}


function generic_update(game_state) {
    var res = game_state["mission_results"];

    $("#footer .mission-circle").each(function(i, el) {
        $(el).removeClass("fail");
        $(el).removeClass("success");

        if (i < res.length) {
            if (res[i]) {
                $(el).addClass("success");
            } else {
                $(el).addClass("fail");
            }
        }
        return 0;
    });

    return 0;
}

/* TODO */
function update_state_empty(game_state) {
    return 0;
}

function update_state_not_started(game_state) {
    return 0;
}

function update_state_waiting_for_mission(game_state) {
    return 0;
}

function update_state_waiting_for_votes(game_state) {
    return 0;
}

function update_state_mission_pending(game_state) {
    return 0;
}

function update_state_lady(game_state) {
    return 0;
}

function update_state_assassin(game_state) {
    return 0;
}

function update_state_finished(game_state) {
    return 0;
}

