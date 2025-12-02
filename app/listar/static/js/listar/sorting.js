export function setupSorting(onSortChange) {
    $(".sort-icon").on("click", function () {
        const column = $(this).data("sort");

        $(".sort-icon").removeClass("fa-sort-up fa-sort-down").addClass("fa-sort");

        let direction = $(this).data("direction") || "desc";
        direction = direction === "desc" ? "asc" : "desc";
        $(this).data("direction", direction);

        $(this)
            .removeClass("fa-sort")
            .addClass(direction === "asc" ? "fa-sort-up" : "fa-sort-down");

        onSortChange(column, direction);
    });
}