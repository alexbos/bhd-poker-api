// ==UserScript==
// @name         BHD Video Poker Help Button
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Button to help determine optimal holds
// @author       bluetardis
// @match        https://beyond-hd.me/games/play/*
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function() {
    'use strict';

    function extractCardFromImageSrc(src) {
        let cardCode = src.split("/").pop().replace(".png", "").toLowerCase();
        if (cardCode.startsWith('10')) {
            cardCode = 't' + cardCode[2];
        }
        return cardCode;
    }

    function extractCardImages() {
        let cards = [];
        for (let i = 0; i < 5; i++) {
            let cardImageElement = document.getElementById(`img${i+1}`);
            if (cardImageElement) {
                let src = cardImageElement.getAttribute('src');
                let card = extractCardFromImageSrc(src);
                cards.push(card);
            }
        }
        return cards.join('');
    }

    function sendHandToAPI(hand) {
        GM_xmlhttpRequest({
            method: "POST",
            url: "http://vpoker.fwdbox.net:2095/analyze-hand",
            data: JSON.stringify({
                hand: hand
            }),
            headers: {
                "Content-Type": "application/json"
            },
            onload: function(response) {
                try {
                    let responseData = JSON.parse(response.responseText);

                    // Check for errors in the API response
                    if (responseData.error) {
                        console.error("API returned an error:", responseData.error);
                        alert("API Error: " + responseData.error);  // Optionally show an alert to the user
                        return;
                    }

                    // Extract the holdKey from the response data
                    let holdKey = Object.keys(responseData)[0];
                    console.log("Extracted hold key from API response:", holdKey);
                    highlightHoldButtons(holdKey);

                } catch (e) {
                    console.error("Error parsing API response:", e);
                }
            },
            onerror: function(err) {
                console.error("Request failed", err);
            }
        });
    }

    function highlightHoldButtons(holdKey) {
        for (let i = 0; i < 5; i++) {
            let cardCode = holdKey.slice(i*2, i*2 + 2);
            let buttonDiv = document.getElementById(`button${i+1}`);
            //console.log(`Evaluating button${i+1} with card code '${cardCode}'`);  // Debugging
            if (buttonDiv && cardCode !== 'XX') {
                //console.log(`Highlighting button${i+1}`);  // Debugging
                let spanElement = buttonDiv.querySelector('span');
                if (spanElement) {
                    spanElement.style.backgroundColor = '#324472';
                }
            }
        }
    }

    function activateScript() {
        let drawButtonTxt = document.getElementById("videopokerSpinTxt");
        if (drawButtonTxt && drawButtonTxt.textContent !== "Draw") {
            return;  // Exit the function if it's not the Draw phase
        }

        let hand = extractCardImages();
        console.log("Extracted cards:", hand);
        sendHandToAPI(hand);
    }

    // Create "Help" button
    let helpButton = document.createElement("button");
    helpButton.innerText = "Help";
    helpButton.style.marginLeft = "10px";
    helpButton.style.padding = "5px 15px";
    helpButton.style.border = "none";
    helpButton.style.borderRadius = "4px";
    helpButton.style.backgroundColor = "#888";
    helpButton.style.color = "#FFF";
    helpButton.style.cursor = "pointer";
    helpButton.onclick = activateScript;

    // Find the container of the "Draw" button and insert the "Help" button after it
    let drawButtonSpan = document.getElementById("videopokerDoSpin");
    if (drawButtonSpan && drawButtonSpan.parentNode) {
        drawButtonSpan.parentNode.insertBefore(helpButton, drawButtonSpan.nextSibling);
    }

})();
