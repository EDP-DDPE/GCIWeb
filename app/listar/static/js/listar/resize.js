// resize.js
export function setupColumnResizing() {
    let isResizing = false;
    let currentColumn = null;
    let startX = 0;
    let startWidth = 0;
    let colIndex = 0;

    $(".resize-handle").off("mousedown").on("mousedown", function (e) {
        e.preventDefault();
        e.stopPropagation();

        isResizing = true;
        currentColumn = $(this).closest("th");
        colIndex = currentColumn.index();
        startX = e.clientX;
        startWidth = currentColumn.outerWidth();

        $(document).on("mousemove.columnResize", handleResize);
        $(document).on("mouseup.columnResize", stopResize);
    });

    function handleResize(e) {
        if (!isResizing) return;

        const newWidth = startWidth + (e.clientX - startX);

        if (newWidth < 60) return;

        currentColumn.css({
            width: newWidth + "px",
            minWidth: newWidth + "px",
            maxWidth: newWidth + "px"
        });

        // sincroniza filtro
        $("#filterRow th").eq(colIndex).css({
            width: newWidth + "px",
            minWidth: newWidth + "px",
            maxWidth: newWidth + "px"
        });

        // sincroniza tbody
        $("#tableBody tr").each(function () {
            $(this).find("td").eq(colIndex).css({
                width: newWidth + "px",
                minWidth: newWidth + "px",
                maxWidth: newWidth + "px"
            });
        });
    }

    function stopResize() {
        isResizing = false;
        $(document).off(".columnResize");
    }
}