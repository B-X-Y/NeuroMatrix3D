const generatingStatus = document.getElementById("generating-status");
const generationError = document.getElementById("generation-error");
const downloadLink = document.getElementById("download-link");
const statusUrl = document.body.dataset.statusUrl;

let stopped = false;

function showGenerating(message) {
    generatingStatus.textContent = message;
    generatingStatus.hidden = false;
    generationError.hidden = true;
    downloadLink.hidden = true;
}

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
            showError("Checking generation status failed.");
            return true;
        }

        const data = await response.json();

        if (data.status === "pending") {
            showGenerating("Generation is queued...");
            return false;
        }

        if (data.status === "running") {
            showGenerating("Generating braille model...");
            return false;
        }

        if (data.status === "done") {
            showDownloadButton();
            return true;
        }

        if (data.status === "error") {
            showError(data.error || "Generation failed.");
            return true;
        }

        if (data.status === "expired") {
            showError(data.error || "Generation job expired. Please generate again.");
            return true;
        }

        showError("Unknown generation status.");
        return true;
    } catch (error) {
        showError("Checking generation status failed.");
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

if (!generatingStatus || !generationError || !downloadLink || !statusUrl) {
    console.error("Download status page is missing required elements.");
} else {
    showGenerating("Preparing generation...");
    void pollGenerationStatus();
}
