// details.js

export function verDetalhes(idEstudo) {
    if (!idEstudo) return;

    const $modalBody = $("#modalDetalhesBody");
    const modalEl = document.getElementById("modalDetalhes");
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

    // Loading enquanto busca
    $modalBody.html(`
        <div class="d-flex justify-content-center p-4">
            <div class="spinner-border text-primary"></div>
        </div>
    `);

    modal.show();

    // Chama o backend que devolve HTML já renderizado
    $.get(`/listar/estudos/${idEstudo}`)
        .done(html => {
            $modalBody.html(html);
        })
        .fail(err => {
            console.error("Erro ao carregar detalhes:", err);
            $modalBody.html(`
                <div class="alert alert-danger">
                    Erro ao carregar detalhes do estudo.
                </div>
            `);
        });
}

// deixa global para funcionar no onclick do botão da tabela
window.verDetalhes = verDetalhes;


// Funções de visualizar a imagem em detalhes

let zoomLevel = 1;
const ZOOM_STEP = 0.08;   // botões
const WHEEL_STEP = 0.02;

let isPanning = false;
let startX = 0;
let startY = 0;
let translateX = 0;
let translateY = 0;

const modalElement = document.getElementById("modalImagem");
const imgElement = document.getElementById("imagemModal");
const container = document.getElementById("imageContainer");

const modalImagem = new bootstrap.Modal(modalElement);

/* ===============================
   Abrir imagem
================================ */
document.addEventListener("click", (event) => {
    const btn = event.target.closest(".ver-imagem-db");
    if (!btn) return;

    const id = btn.dataset.id;
    if (!id) return;

    // Reset
    zoomLevel = 1;
    const rect = container.getBoundingClientRect();
    translateX = rect.width / 2 - imgElement.naturalWidth / 2;
    translateY = rect.height / 2 - imgElement.naturalHeight / 2;
    aplicarTransform();

    imgElement.src = `/listar/imagem/${id}`;
    imgElement.draggable = false; //

    modalImagem.show();
});

/* ===============================
   Zoom
================================ */
document.getElementById("zoomIn").addEventListener("click", () => {
    zoomLevel += ZOOM_STEP;
    aplicarTransform();
});

document.getElementById("zoomOut").addEventListener("click", () => {
    zoomLevel = Math.max(0.2, zoomLevel - ZOOM_STEP);
    aplicarTransform();
});

document.getElementById("zoomReset").addEventListener("click", () => {
    zoomLevel = 1;
    translateX = 0;
    translateY = 0;
    aplicarTransform();
});

/* ===============================
   Scroll zoom
================================ */
modalElement.addEventListener("wheel", (e) => {
    e.preventDefault();

    const direction = e.deltaY < 0 ? 1 : -1;
    zoomLevel += direction * WHEEL_STEP;
    zoomLevel = Math.max(0.2, Math.min(zoomLevel, 6));

    aplicarTransform();
}, { passive: false });

/* ===============================
   PAN (arrastar imagem)
================================ */
container.addEventListener("mousedown", (e) => {
    isPanning = true;
    startX = e.clientX - translateX;
    startY = e.clientY - translateY;
    container.style.cursor = "grabbing";
});

document.addEventListener("mousemove", (e) => {
    if (!isPanning) return;

    translateX = e.clientX - startX;
    translateY = e.clientY - startY;
    aplicarTransform();
});

document.addEventListener("mouseup", () => {
    isPanning = false;
    container.style.cursor = "grab";
});

/* ===============================
   Aplica zoom + pan
================================ */
function aplicarTransform() {
    imgElement.style.transform =
        `translate(${translateX}px, ${translateY}px) scale(${zoomLevel})`;
}

imgElement.addEventListener("load", () => {
    const containerRect = container.getBoundingClientRect();
    const imgRect = imgElement.getBoundingClientRect();

    translateX = (containerRect.width - imgRect.width) / 2;
    translateY = (containerRect.height - imgRect.height) / 2;

    aplicarTransform();
});
