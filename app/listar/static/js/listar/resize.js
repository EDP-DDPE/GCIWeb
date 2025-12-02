// resize.js
export function setupColumnResizing() {
    let isResizing = false;
    let currentColumn = null;
    let startX = 0;
    let startWidth = 0;

    $(".resize-handle").on("mousedown", function (e) {
        e.preventDefault();
        isResizing = true;
        currentColumn = $(this).closest("th");
        startX = e.clientX;
        startWidth = parseInt(currentColumn.css("width"), 10);

        $(document).on("mousemove", handleResize);
        $(document).on("mouseup", stopResize);
    });

    function handleResize(e) {
        if (!isResizing) return;
        const width = startWidth + e.clientX - startX;
        currentColumn.css("width", width + "px");
    }

    function stopResize() {
        isResizing = false;
        $(document).off("mousemove", handleResize);
        $(document).off("mouseup", stopResize);
    }
}
