// Widget flutuante do Atlas GPT — presente em todas as páginas via base.html.
// Usa as mesmas APIs do chat completo (/api/llm_query, /api/save_chat, /api/load_chat),
// então as conversas ficam salvas no histórico do Atlas GPT normalmente.
(function () {
    const STORAGE_CHAT_ID = "atlasWidget.chatId";
    const STORAGE_OPEN = "atlasWidget.open";

    const toggleBtn = document.getElementById("atlas-widget-toggle");
    const panel = document.getElementById("atlas-widget-panel");
    if (!toggleBtn || !panel) return;

    const messagesBox = document.getElementById("atlas-widget-messages");
    const input = document.getElementById("atlas-widget-input");
    const sendBtn = document.getElementById("atlas-widget-send");
    const typingIndicator = document.getElementById("atlas-widget-typing");
    const newChatBtn = document.getElementById("atlas-widget-new");
    const closeBtn = document.getElementById("atlas-widget-close");

    let currentChatId = sessionStorage.getItem(STORAGE_CHAT_ID) || null;
    let autoSaveTimer = null;
    let messageCount = 0;

    // downloadCSV é usado nos botões dentro do HTML gerado pelo bot
    if (!window.downloadCSV) {
        window.downloadCSV = function (filename, chatId) {
            window.open(`/api/download_csv/${chatId}/${filename}`, "_blank");
        };
    }

    // ---------------------------
    // Abrir / fechar
    // ---------------------------
    function openPanel() {
        panel.classList.remove("aw-hidden");
        sessionStorage.setItem(STORAGE_OPEN, "1");
        messagesBox.scrollTop = messagesBox.scrollHeight;
        input.focus();
    }

    function closePanel() {
        panel.classList.add("aw-hidden");
        sessionStorage.setItem(STORAGE_OPEN, "0");
    }

    toggleBtn.addEventListener("click", () => {
        if (panel.classList.contains("aw-hidden")) openPanel();
        else closePanel();
    });

    closeBtn.addEventListener("click", closePanel);

    // ---------------------------
    // Mensagens
    // ---------------------------
    function showEmptyState() {
        messagesBox.innerHTML = `
            <div class="aw-empty">
                <div class="aw-empty-icon">💭</div>
                <div>Olá! Sou o Atlas. Como posso ajudar?</div>
            </div>
        `;
    }

    function appendMessage(text, role, html = null, sql = null) {
        const emptyState = messagesBox.querySelector(".aw-empty");
        if (emptyState) emptyState.remove();

        const div = document.createElement("div");
        div.classList.add("aw-message", role);

        const textDiv = document.createElement("div");
        textDiv.classList.add("aw-message-text");
        textDiv.innerHTML = text;
        div.appendChild(textDiv);

        if (sql) {
            const sqlBox = document.createElement("div");
            sqlBox.classList.add("code-block");
            sqlBox.innerHTML = `
                <div class="code-header" onclick="this.nextElementSibling.classList.toggle('open')">
                    <span>📄 Código executado</span>
                    <button class="toggle-btn">Mostrar/Ocultar</button>
                </div>
                <pre class="code-content"><code>${sql}</code></pre>
            `;
            div.appendChild(sqlBox);
        }

        if (html) {
            const htmlDiv = document.createElement("div");
            htmlDiv.classList.add("aw-html-content");
            htmlDiv.innerHTML = html;
            div.appendChild(htmlDiv);

            // Renderiza gráficos Chart.js embutidos no HTML do bot
            setTimeout(() => {
                const scripts = htmlDiv.querySelectorAll("script");
                scripts.forEach(s => eval(s.textContent));

                const canvas = htmlDiv.querySelector("canvas");
                if (!canvas) return;

                const data = window["renderChart_" + canvas.id];
                if (!data || typeof Chart === "undefined") return;

                new Chart(canvas.getContext("2d"), {
                    type: "line",
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: "Valores",
                            data: data.dataset,
                            borderColor: "rgba(75, 192, 192, 1)",
                            backgroundColor: "rgba(75, 192, 192, 0.2)",
                            tension: 0.25
                        }]
                    },
                    options: { responsive: true }
                });
            }, 20);
        }

        messagesBox.appendChild(div);
        messagesBox.scrollTop = messagesBox.scrollHeight;

        messageCount++;
        scheduleAutoSave();
    }

    // ---------------------------
    // Envio
    // ---------------------------
    function sendMessage() {
        const msg = input.value.trim();
        if (!msg) return;

        appendMessage(msg, "user");
        input.value = "";
        input.style.height = "auto";
        sendBtn.disabled = true;
        typingIndicator.classList.add("active");

        fetch("/api/llm_query", {
            method: "POST",
            body: JSON.stringify({ prompt: msg, chat_id: currentChatId }),
            headers: { "Content-Type": "application/json" }
        })
        .then(r => r.json())
        .then(data => {
            typingIndicator.classList.remove("active");
            sendBtn.disabled = false;

            if (data.chat_id) {
                currentChatId = data.chat_id;
                sessionStorage.setItem(STORAGE_CHAT_ID, currentChatId);
            }

            appendMessage(data.text || "(sem texto)", "bot", data.html || null, data.sql || null);
            input.focus();
        })
        .catch(err => {
            typingIndicator.classList.remove("active");
            sendBtn.disabled = false;
            console.error("Erro:", err);
            appendMessage(
                "⚠️ Ocorreu um erro ao processar sua solicitação. Tente novamente em alguns segundos.",
                "bot"
            );
        });
    }

    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Textarea cresce conforme o texto
    input.addEventListener("input", function () {
        this.style.height = "auto";
        this.style.height = Math.min(this.scrollHeight, 90) + "px";
    });

    // ---------------------------
    // Salvamento (mesmo mecanismo do chat completo)
    // ---------------------------
    function scheduleAutoSave() {
        if (autoSaveTimer) clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(saveChat, 2000);
    }

    function saveChat() {
        if (!currentChatId) return;

        fetch("/api/save_chat", {
            method: "POST",
            body: JSON.stringify({ chat_id: currentChatId }),
            headers: { "Content-Type": "application/json" }
        }).catch(err => console.error("Erro ao salvar chat:", err));
    }

    window.addEventListener("beforeunload", () => {
        if (messageCount > 0 && currentChatId) {
            navigator.sendBeacon(
                "/api/save_chat",
                new Blob([JSON.stringify({ chat_id: currentChatId })], { type: "application/json" })
            );
        }
    });

    // ---------------------------
    // Nova conversa
    // ---------------------------
    newChatBtn.addEventListener("click", () => {
        currentChatId = null;
        messageCount = 0;
        sessionStorage.removeItem(STORAGE_CHAT_ID);
        showEmptyState();
        input.focus();
    });

    // ---------------------------
    // Restaurar conversa ao trocar de página
    // ---------------------------
    function restoreChat() {
        if (!currentChatId) return;

        fetch(`/api/load_chat/${currentChatId}`)
        .then(r => {
            if (!r.ok) throw new Error("Chat não encontrado");
            return r.json();
        })
        .then(data => {
            if (!data.messages || data.messages.length === 0) return;

            messagesBox.innerHTML = "";
            data.messages.forEach(msg => {
                appendMessage(msg.text, msg.role, msg.html || null, msg.sql || null);
            });
            // Restaurar não conta como atividade nova
            if (autoSaveTimer) clearTimeout(autoSaveTimer);
            messageCount = 0;
        })
        .catch(() => {
            currentChatId = null;
            sessionStorage.removeItem(STORAGE_CHAT_ID);
        });
    }

    restoreChat();

    if (sessionStorage.getItem(STORAGE_OPEN) === "1") {
        panel.classList.remove("aw-hidden");
    }
})();
