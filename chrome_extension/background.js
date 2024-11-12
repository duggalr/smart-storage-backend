
// Context Menu
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "save_web_page",
        title: "Save Web Page",
        contexts: ["all"]
    });
});
  
// Event Listeners for Context Menu
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "save_web_page" && tab.id) {
        console.log("test");

        chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
            // Define the metadata
            const metadata = {
                url: tab.url,
                title: tab.title,
                description: ""
            };

            // Execute script in the tab context, passing dataUrl and metadata
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: ({ dataUrl, metadata }) => {
                    // console.log("dataUrl:", dataUrl);
                    // console.log("Metadata:", metadata);

                    let rv = {
                        'data_url': dataUrl,
                        'metadata': metadata
                    };

                    fetch("http://127.0.0.1:8000/process_user_save_request", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(rv)
                    });
                },
                args: [{ dataUrl, metadata }]
            });
        });
    }
});
