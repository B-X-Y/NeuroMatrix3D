function getViewerFrame() {
    return document.getElementById("viewerFrame");
}

function reloadViewer() {
    const iframe = getViewerFrame();

    if (!iframe || !iframe.contentWindow) {
        return;
    }

    iframe.contentWindow.location.reload();
}

function fullscreenViewer() {
    const iframe = getViewerFrame();

    if (!iframe) {
        return;
    }

    if (iframe.requestFullscreen) {
        iframe.requestFullscreen();
    } else if (iframe.webkitRequestFullscreen) {
        iframe.webkitRequestFullscreen();
    } else if (iframe.msRequestFullscreen) {
        iframe.msRequestFullscreen();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const reloadButton = document.querySelector('[data-action="reload-viewer"]');
    const fullscreenButton = document.querySelector('[data-action="fullscreen-viewer"]');

    if (reloadButton) {
        reloadButton.addEventListener("click", reloadViewer);
    }

    if (fullscreenButton) {
        fullscreenButton.addEventListener("click", fullscreenViewer);
    }
});
