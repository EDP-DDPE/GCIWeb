// alternativa-download.js — modal de opções + download do modelo preenchido

let _idEstudoDownload = null;

export function abrirModalDownload(idEstudo) {
    _idEstudoDownload = idEstudo;

    document.querySelectorAll('#modalDownloadOpcoes input[type="radio"]')
        .forEach(r => r.checked = false);

    ["erro_etapas", "erro_alternativa", "erro_fluxo"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = "none";
    });

    bootstrap.Modal.getOrCreateInstance(
        document.getElementById("modalDownloadOpcoes")
    ).show();
}

export async function confirmarDownload(e) {
    if (e) e.preventDefault();

    const multiplas_etapas = document.querySelector('input[name="multiplas_etapas"]:checked');
    const alternativa_unica = document.querySelector('input[name="alternativa_unica"]:checked');
    const fluxo_reverso = document.querySelector('input[name="fluxo_reverso"]:checked');

    const erroEtapas = document.getElementById("erro_etapas");
    const erroAlternativa = document.getElementById("erro_alternativa");
    const erroFluxo = document.getElementById("erro_fluxo");

    let valido = true;

    if (!multiplas_etapas) {
        if (erroEtapas) erroEtapas.style.display = "block";
        valido = false;
    } else if (erroEtapas) {
        erroEtapas.style.display = "none";
    }

    if (!alternativa_unica) {
        if (erroAlternativa) erroAlternativa.style.display = "block";
        valido = false;
    } else if (erroAlternativa) {
        erroAlternativa.style.display = "none";
    }

    // valida fluxo reverso apenas se a pergunta existir
    if (document.querySelector('input[name="fluxo_reverso"]')) {
        if (!fluxo_reverso) {
            if (erroFluxo) erroFluxo.style.display = "block";
            valido = false;
        } else if (erroFluxo) {
            erroFluxo.style.display = "none";
        }
    }

    if (!valido) return;

    const fluxoValor = fluxo_reverso ? fluxo_reverso.value : "nao";

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

        const disposition = response.headers.get("Content-Disposition") || "";
        const utf8Match = disposition.match(/filename\*=UTF-8''([^;\n]+)/i);
        const plainMatch = disposition.match(/filename="?([^";\n]+)"?/i);
        const filename = utf8Match
            ? decodeURIComponent(utf8Match[1])
            : plainMatch ? plainMatch[1] : "documento.docx";

        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = filename;
        a.dataset.noLoading = "true";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);

        bootstrap.Modal.getOrCreateInstance(
            document.getElementById("modalDownloadOpcoes")
        ).hide();

    } catch (err) {
        console.error("Erro no download:", err);
        alert("Erro inesperado: " + err.message);
    }
}

// Expor para os onclick do HTML
window.abrirModalDownload = abrirModalDownload;
window.confirmarDownload = confirmarDownload;