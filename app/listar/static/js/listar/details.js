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


let _idEstudoDownload = null;

function abrirModalDownload(idEstudo) {
    _idEstudoDownload = idEstudo;

    // Limpa seleções anteriores
    document.querySelectorAll('input[name="multiplas_etapas"]').forEach(r => r.checked = false);
    document.querySelectorAll('input[name="alternativa_unica"]').forEach(r => r.checked = false);
    document.getElementById('erro_etapas').style.display = 'none';
    document.getElementById('erro_alternativa').style.display = 'none';

    const modal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById('modalDownloadOpcoes')
    );
    modal.show();
}

window.abrirModalDownload = abrirModalDownload;

async function confirmarDownload(e) {

    if (e) e.preventDefault();

    const multiplas_etapas = document.querySelector('input[name="multiplas_etapas"]:checked');
    const alternativa_unica = document.querySelector('input[name="alternativa_unica"]:checked');
    const fluxo_reverso = document.querySelector('input[name="fluxo_reverso"]:checked');

    let valido = true;

    // ✅ declarações que estavam faltando
    const erroEtapas = document.getElementById('erro_etapas');
    const erroAlternativa = document.getElementById('erro_alternativa');
    const erroFluxo = document.getElementById('erro_fluxo');

    if (!multiplas_etapas) {
        if (erroEtapas) erroEtapas.style.display = 'block';
        valido = false;
    } else if (erroEtapas) {
        erroEtapas.style.display = 'none';
    }

    if (!alternativa_unica) {
        if (erroAlternativa) erroAlternativa.style.display = 'block';
        valido = false;
    } else if (erroAlternativa) {
        erroAlternativa.style.display = 'none';
    }

    // ✅ valida fluxo reverso apenas se a pergunta existir
    if (document.querySelector('input[name="fluxo_reverso"]')) {
        if (!fluxo_reverso) {
            if (erroFluxo) erroFluxo.style.display = 'block';
            valido = false;
        } else if (erroFluxo) {
            erroFluxo.style.display = 'none';
        }
    }

    if (!valido) return;

    // ✅ valor padrão quando fluxo_reverso não existe
    const fluxoValor = fluxo_reverso ? fluxo_reverso.value : 'nao';

    // ✅ URL correta (sem &amp;)
    const url =
        `/listar/estudos/${_idEstudoDownload}/download_template` +
        `?multiplas_etapas=${multiplas_etapas.value}` +
        `&alternativa_unica=${alternativa_unica.value}` +
        `&fluxo_reverso=${fluxoValor}`;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            let errorMsg = "Erro ao gerar documento.";
            try {
                const data = await response.json();
                errorMsg = data.error || errorMsg;
            } catch (_) {}
            alert(errorMsg);
            return;
        }

        const blob = await response.blob();
        if (!blob || blob.size === 0) {
            alert("O arquivo retornou vazio.");
            return;
        }

        const disposition = response.headers.get('Content-Disposition') || '';
        const utf8Match = disposition.match(/filename\*=UTF-8''([^;\n]+)/i);
        const plainMatch = disposition.match(/filename="?([^";\n]+)"?/i);
        const filename = utf8Match
            ? decodeURIComponent(utf8Match[1])
            : plainMatch
                ? plainMatch[1]
                : 'documento.docx';

        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);

        document.querySelectorAll('#modalDownloadOpcoes input[type="radio"]')
            .forEach(radio => radio.checked = false);
        if (erroEtapas) erroEtapas.style.display = 'none';
        if (erroAlternativa) erroAlternativa.style.display = 'none';
        if (erroFluxo) erroFluxo.style.display = 'none';

        bootstrap.Modal.getOrCreateInstance(
            document.getElementById('modalDownloadOpcoes')
        ).hide();

    } catch (err) {
        console.error("Erro no download:", err);
        alert("Erro inesperado: " + err.message);
    }
}


window.confirmarDownload = confirmarDownload;
