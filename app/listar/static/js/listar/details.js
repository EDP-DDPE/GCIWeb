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
