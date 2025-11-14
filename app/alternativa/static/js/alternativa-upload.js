export function inicializarUploadImagem() {

    const dropZone = $("#drop_zone");
    const fileInput = $("#imagem_alternativa");
    const preview = $("#preview_imagem");

    dropZone.on("click", () => fileInput.click());

    fileInput.on("change", () => handleFiles(fileInput[0].files));

    dropZone.on("dragover", e => {
        e.preventDefault();
        dropZone.css("background", "#e9ecef");
    });

    dropZone.on("dragleave", e => {
        e.preventDefault();
        dropZone.css("background", "");
    });

    dropZone.on("drop", e => {
        e.preventDefault();
        dropZone.css("background", "");
        handleFiles(e.originalEvent.dataTransfer.files);
    });

    function handleFiles(files) {
        if (!files.length) return;

        const file = files[0];
        if (!file.type.startsWith("image/")) {
            alert("Apenas imagens são permitidas");
            return;
        }

        const reader = new FileReader();
        reader.onload = e => {
            preview.attr("src", e.target.result).show();
        };
        reader.readAsDataURL(file);

        // coloca o arquivo no input WTForms
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput[0].files = dt.files;
    }
}
