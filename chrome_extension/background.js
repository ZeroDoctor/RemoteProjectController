console.log('backgound script is running...')
// could generate this path var later
var path = "file:///C:/Users/danie/Documents/AutoInterface/chrome_extension/tabpage/get_tabs.html";

let tabUpdateHandler = (tabId, {
	url: updatedUrl,
	status
}, tab) => {
	if (updatedUrl == path) {
		console.log('grabbing all current tabs')
		chrome.tabs.query({}, function (tabs) {

			var urls = tabs.map(function (tab) {
				return tab.url;
			});

			sendToServer(urls);
		});
	}
}

chrome.tabs.onUpdated.addListener(tabUpdateHandler);

function sendToServer(urls) {
	console.log(urls);

	var ws = new WebSocket('ws://127.0.0.1:8080/');
	ws.onopen = function () {
		console.log('connection established');
		ws.send(urls);
		console.log('message was sent');
	}

	ws.onclose = function (event) {
		if (event.wasClean) {
			console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
		} else {
			console.log('[close] Connection died');
		}
	};
}
