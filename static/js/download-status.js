const generatingStatus = document.getElementById("generating-status");
const generationError = document.getElementById("generation-error");
const downloadLink = document.getElementById("download-link");
const statusUrl = document.body.dataset.statusUrl;

let stopped = false;

function showDownloadButton() {
    generatingStatus.hidden = true;
    generationError.hidden = true;
    downloadLink.hidden = false;
}

function showError(message) {
    generatingStatus.hidden = true;
    downloadLink.hidden = true;
    generationError.textContent = message;
    generationError.hidden = false;
}

async function checkGenerationStatus() {
    try {
        const response = await fetch(statusUrl, {cache: "no-store"});

        if (!response.ok) {
            showError("Could not check generation status.");
            return true;
        }

        const data = await response.json();

        if (data.status === "done") {
            showDownloadButton();
            return true;
        }

        if (data.status === "error") {
            showError(data.error || "Generation failed.");
            return true;
        }

        return false;
    } catch (_error) {
        showError("Could not check generation status.");
        return true;
    }
}

async function pollGenerationStatus() {
    if (stopped) return;

    const finished = await checkGenerationStatus();

    if (finished) {
        stopped = true;
        return;
    }

    setTimeout(pollGenerationStatus, 1000);
}

pollGenerationStatus();
