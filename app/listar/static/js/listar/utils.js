// utils.js
export function initializeTooltips() {
    if (bootstrap?.Tooltip) {
        $("[data-bs-toggle='tooltip']").each(function () {
            new bootstrap.Tooltip(this);
        });
    }
}

//export function showLoading() {
//    $("#loadingOverlay").show();
//}
//
//export function hideLoading() {
//    $("#loadingOverlay").hide();
//}

export function debounce(fn, delay = 400) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), delay);
    };
}
