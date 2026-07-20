// documentos.js — Documentos Padronizados (fluxo normal e fluxo reverso)
import { loadData } from "./table.js";

let tipoSolicitacaoIdDocumento = null;

function getAlertaRevisao(dataAtualizacaoStr) {
    if (!dataAtualizacaoStr) return null;

    // Converte "DD/MM/YYYY HH:MM" para Date
    const partes = dataAtualizacaoStr.split(" ")[0].split("/");
    const dataAtualizacao = new Date(`${partes[2]}-${partes[1]}-${partes[0]}`);
    const hoje = new Date();

    // Data limite = atualização + 6 meses
    const dataLimite = new Date(dataAtualizacao);
    dataLimite.setMonth(dataLimite.getMonth() + 6);

    const diffMs = dataLimite - hoje;
    const diffDias = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDias < 0) {
        return {
            tipo: "danger",
            icone: "bi-exclamation-triangle-fill",
            mensagem: `Documento vencido há ${Math.abs(diffDias)} dia(s). Revisão obrigatória!`
        };
    } else if (diffDias <= 30) {
        return {
            tipo: "warning",
            icone: "bi-clock-fill",
            mensagem: `Documento vence em ${diffDias} dia(s). Revisão recomendada!`
        };
    }
    return {
        tipo: "success",
        icone: "bi-check-circle-fill",
        mensagem: `Documento em dia. Próxima revisão em ${diffDias} dia(s) (${dataLimite.toLocaleDateString("pt-BR")}).`
    };
}

export function abrirModalDocumento(tipoId, fluxoReverso = 0) {
    tipoSolicitacaoIdDocumento = tipoId;

    const $modalBody = fluxoReverso === 0
        ? $("#modalDocumentoBody")
        : $("#modalDocumentoInversoBody");

    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 150px;">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal(
        fluxoReverso === 0
            ? $("#modalDocumento")[0]
            : $("#modalDocumentoInverso")[0]
    );

    modal.show();

    $.get(`/tipo_solicitacao/${tipoId}/api?fluxo_reverso=${fluxoReverso}`)
        .done(function (data) {
            const doc = data.doc_padronizado;

            let docHtml = "";
            if (doc) {
                const alerta = getAlertaRevisao(doc.data_atualizacao);
                const alertaHtml = alerta ? `
                    <div class="alert alert-${alerta.tipo} d-flex align-items-center py-2 mb-3">
                        <i class="bi ${alerta.icone} me-2 fs-5"></i>
                        <span>${alerta.mensagem}</span>
                    </div>
                ` : "";

                docHtml = `
                    ${alertaHtml}
                    <p><strong>Documento atual:</strong> ${doc.nome_doc || "(sem nome)"}</p>
                    <p><strong>Tipo:</strong> ${doc.tipo_doc || "-"}</p>
                    <p><strong>Criado em:</strong> ${doc.data_criacao || "-"}</p>
                    <p><strong>Última atualização:</strong> ${doc.data_atualizacao || "-"}</p>
                    <p><strong>Total de versões:</strong> ${doc.total_versoes}</p>
                    <button class="btn btn-sm btn-outline-primary mb-2" onclick="baixarDocumentoAtual(${fluxoReverso})">
                        <i class="bi bi-download"></i> Baixar atual
                    </button>
                `;
            } else {
                docHtml = `
                    <div class="alert alert-warning">
                        Nenhum documento padrão cadastrado para este tipo de solicitação.
                    </div>
                `;
            }

            $modalBody.html(`
                <div class="mb-3">
                    <h6>Tipo de Solicitação ${data.id}</h6>
                    <p><strong>Viabilidade:</strong> ${data.viabilidade || "-"}</p>
                    <p><strong>Análise:</strong> ${data.analise || "-"}</p>
                    <p><strong>Pedido:</strong> ${data.pedido || "-"}</p>
                </div>
                <hr>
                <div class="mb-3">
                    ${docHtml}
                </div>
                <hr>
                <div class="mb-2">
                    <h6>Versões anteriores</h6>
                    <div class="listaVersoesDoc">
                        Carregando versões...
                    </div>
                </div>
            `);

            carregarVersoesDocumento(fluxoReverso);
        })
        .fail(function () {
            $modalBody.html('<div class="alert alert-danger">Erro ao carregar informações do documento.</div>');
        });
}

export function carregarVersoesDocumento(fluxoReverso = 0) {
    if (!tipoSolicitacaoIdDocumento) return;

    const $modalBody = fluxoReverso === 0
        ? $("#modalDocumentoBody")
        : $("#modalDocumentoInversoBody");
    const $lista = $modalBody.find(".listaVersoesDoc");

    $.get(`/tipo_solicitacao/${tipoSolicitacaoIdDocumento}/documento/versoes?fluxo_reverso=${fluxoReverso}`)
        .done(function (resp) {
            if (resp.status !== "success") {
                $lista.html('<div class="alert alert-danger">Erro ao carregar versões.</div>');
                return;
            }

            const versoes = resp.versoes || [];
            if (versoes.length === 0) {
                $lista.html('<p class="text-muted mb-0">Nenhuma versão anterior encontrada.</p>');
                return;
            }

            let html = `
                <table class="table table-sm table-bordered mb-0">
                    <thead class="table-light">
                        <tr>
                            <th style="width: 80px;">Versão</th>
                            <th>Nome</th>
                            <th style="width: 180px;">Data atualização</th>
                            <th style="width: 80px;">Ações</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            versoes.forEach(v => {
                html += `
                    <tr>
                        <td class="text-center">${v.versao}</td>
                        <td>${v.nome_doc}</td>
                        <td>${v.data_atualizacao || "-"}</td>
                        <td class="text-center">
                            <button class="btn btn-sm btn-outline-secondary" onclick="baixarVersaoDocumento(${v.id})">
                                <i class="bi bi-download"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });

            html += "</tbody></table>";
            $lista.html(html);
        })
        .fail(function () {
            $lista.html('<div class="alert alert-danger">Erro ao carregar versões.</div>');
        });
}

export function enviarDocumentoPadrao(fluxoReverso = 0) {
    if (!tipoSolicitacaoIdDocumento) return;

    const inputArquivo = fluxoReverso === 0
        ? $("#arquivoDocumento")
        : $("#arquivoDocumentoInverso");

    const arquivo = inputArquivo[0].files[0];

    if (!arquivo) {
        alert("Selecione um arquivo para enviar.");
        return;
    }

    const formData = new FormData();
    formData.append("arquivo", arquivo);

    $.ajax({
        url: `/tipo_solicitacao/${tipoSolicitacaoIdDocumento}/documento/upload?fluxo_reverso=${fluxoReverso}`,
        method: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (resp) {
            if (resp.status === "success") {
                alert("Documento enviado com sucesso.");

                const modalEl = document.getElementById(
                    fluxoReverso === 0 ? "modalDocumento" : "modalDocumentoInverso"
                );
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide(); // o hidden.bs.modal já limpa o input de arquivo

                loadData(); // atualiza o badge da coluna Doc. Padrão sem recarregar a página
            } else {
                alert(resp.message || "Erro ao enviar documento.");
            }
        },
        error: function () {
            alert("Erro ao enviar documento. Tente novamente.");
        }
    });
}

export function baixarDocumentoAtual(fluxoReverso = 0) {
    if (!tipoSolicitacaoIdDocumento) return;
    window.location.href = `/tipo_solicitacao/${tipoSolicitacaoIdDocumento}/documento/download?fluxo_reverso=${fluxoReverso}`;
}

export function baixarVersaoDocumento(idVersao) {
    window.location.href = `/tipo_solicitacao/documento/versao/${idVersao}/download`;
}

// Expor para os onclick do HTML (tabela e conteúdo gerado via JS)
window.abrirModalDocumento = abrirModalDocumento;
window.enviarDocumentoPadrao = enviarDocumentoPadrao;
window.baixarDocumentoAtual = baixarDocumentoAtual;
window.baixarVersaoDocumento = baixarVersaoDocumento;