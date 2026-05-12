        const input = document.getElementById("chat-input");
        const chatBox = document.getElementById("chat-box");
        const sendBtn = document.getElementById("send-btn");
        const typingIndicator = document.getElementById("typing-indicator");
        const autoSaveIndicator = document.getElementById("auto-save");

        let currentChatId = null;
        let autoSaveTimer = null;
        let messageCount = 0;

        // Carregar histórico ao iniciar
        loadChatHistory();

        // Event listeners
        sendBtn.addEventListener("click", sendMessage);
        input.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendMessage();
        });

        function appendMessage(text, role, attachments = [], html = null, sql = null) {
            // Remove empty state se existir
            const emptyState = chatBox.querySelector('.empty-state');
            if (emptyState) emptyState.remove();

            const div = document.createElement("div");
            div.classList.add("message", role);

            const textDiv = document.createElement("div");
            textDiv.classList.add("message-text");
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
                htmlDiv.classList.add("html-content");
                htmlDiv.innerHTML = html;
                div.appendChild(htmlDiv);

                // Se existir canvas com dados de gráfico
                setTimeout(() => {
                    const scripts = htmlDiv.querySelectorAll("script");
                    scripts.forEach(s => eval(s.textContent));

                    const canvas = htmlDiv.querySelector("canvas");
                    if (!canvas) return;

                    const chartId = canvas.id;
                    const data = window["renderChart_" + chartId];

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

//            // Se houver anexos (tabelas/gráficos), cria uma área para eles
//            if (attachments && attachments.length > 0) {
//                const attachContainer = document.createElement("div");
//                attachContainer.classList.add("attachment-container");
//
//                attachments.forEach(att => {
//                    const btn = document.createElement("button");
//                    btn.classList.add("attachment-pill");
//
//                    if (att.type === "table") {
//                        btn.innerText = `📄 ${att.name || 'Tabela'}`;
//                    } else if (att.type === "chart") {
//                        btn.innerText = `📊 ${att.name || 'Gráfico'}`;
//                    } else {
//                        btn.innerText = `📎 ${att.name || 'Anexo'}`;
//                    }
//
//                    btn.onclick = () => openAttachment(att.type, att.id);
//                    attachContainer.appendChild(btn);
//                });
//
//                div.appendChild(attachContainer);
//            }

            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;

            messageCount++;

            // Auto-save após cada troca de mensagens
            scheduleAutoSave();
        }

        function downloadCSV(filename, chatId) {
            const url = `/api/download_csv/${chatId}/${filename}`;
            window.open(url, "_blank");
        }

        function sendMessage() {
            const msg = input.value.trim();
            if (!msg) return;

            appendMessage(msg, "user");
            input.value = "";
            sendBtn.disabled = true;
            typingIndicator.classList.add("active");

            fetch("/api/llm_query", {
                method: "POST",
                body: JSON.stringify({
                    prompt: msg,
                    chat_id: currentChatId
                }),
                headers: { "Content-Type": "application/json" }
            })
            .then(r => r.json())
            .then(data => {
                typingIndicator.classList.remove("active");
                sendBtn.disabled = false;

                // Atualiza o chat_id se for novo
                if (data.chat_id) {
                    currentChatId = data.chat_id;
                }

                // texto do bot
                const botText = data.text || "(sem texto)";

                const sqlText = data.sql || "";

                // anexos futuros (tabelas, gráficos, código...)
                const attachments = data.attachments || [];

                appendMessage(botText, "bot", attachments, data.html || null, sqlText || null);

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

        function scheduleAutoSave() {
            // Limpa timer anterior
            if (autoSaveTimer) {
                clearTimeout(autoSaveTimer);
            }

            // Salva após 2 segundos de inatividade
            autoSaveTimer = setTimeout(() => {
                saveChat(true);
            }, 2000);
        }

        function saveChat(isAutoSave = false) {
            if (!currentChatId && messageCount === 0) return;

            fetch("/api/save_chat", {
                method: "POST",
                body: JSON.stringify({ chat_id: currentChatId }),
                headers: { "Content-Type": "application/json" }
            })
            .then(r => r.json())
            .then(data => {
                if (isAutoSave) {
                    showAutoSaveIndicator();
                }
                loadChatHistory();
            });
        }

        function showAutoSaveIndicator() {
            autoSaveIndicator.classList.add("active");
            setTimeout(() => {
                autoSaveIndicator.classList.remove("active");
            }, 2000);
        }

        function loadChatHistory() {
            fetch("/api/chat_history")
            .then(r => r.json())
            .then(data => {
                const historyContainer = document.getElementById("chat-history");
                historyContainer.innerHTML = "";

                if (data.chats && data.chats.length > 0) {
                    data.chats.forEach(chat => {
                        const item = document.createElement("div");
                        item.classList.add("chat-history-item");
                        if (chat.id === currentChatId) {
                            item.classList.add("active");
                        }

                        item.innerHTML = `
                            <div class="chat-title">${chat.title || 'Conversa sem título'}</div>
                                <div class="row">
                                    <div class="col-6">
                                        <div class="chat-date">${formatDate(chat.date)}</div>
                                    </div>
                                    <div class="col-6">
                                        <div class="chat-actions">
                                            <button class="rename-btn" onclick="renameChat(event, '${chat.id}')"> <i class="bi bi-pencil"></i> </button>
                                            <button class="delete-btn" onclick="deleteChat(event, '${chat.id}')">🗑</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;

                        item.onclick = (e) => loadChat(chat.id, e.currentTarget);
                        historyContainer.appendChild(item);
                    });
                } else {
                    historyContainer.innerHTML = '<div style="color: #6b7c93; text-align: center; padding: 20px;">Nenhuma conversa ainda</div>';
                }
            });
        }

        function loadChat(chatId, elementClicked = null) {
            fetch(`/api/load_chat/${chatId}`)
            .then(r => r.json())
            .then(data => {
                chatBox.innerHTML = "";
                currentChatId = chatId;
                messageCount = 0;

                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        appendMessage(msg.text, msg.role, msg.attachments || [],
                        msg.html || null, msg.sql || null);
                    });
                }

                // Atualizar item ativo no histórico
                document.querySelectorAll('.chat-history-item').forEach(item => {
                    item.classList.remove('active');
                });
//                event.target.closest('.chat-history-item').classList.add('active');
                    document.querySelectorAll('.chat-history-item').forEach(i => {
                        i.classList.remove('active');
                    });

                    if (elementClicked) {
                        elementClicked.classList.add('active');
                    }
            });
        }

        function openAttachment(type, attachmentId) {
            // Aqui você decide o que fazer:
            // - abrir tabela em modal
            // - abrir gráfico em nova aba
            // - download de arquivo, etc.
            //
            // Por enquanto, só um alerta para indicar que está funcionando.
            alert(`Abrir ${type} com id: ${attachmentId} (futuro comportamento aqui)`);
        }

        function startNewChat() {
            currentChatId = null;
            messageCount = 0;
            chatBox.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">💭</div>
                    <div class="empty-state-text">Comece uma nova conversa</div>
                </div>
            `;

            document.querySelectorAll('.chat-history-item').forEach(item => {
                item.classList.remove('active');
            });

            input.focus();
        }

        function deleteChat(event, chatId) {
            event.stopPropagation();

            if (!confirm("Tem certeza que deseja excluir esta conversa?")) return;

            fetch("/api/delete_chat", {
                method: "POST",
                body: JSON.stringify({ chat_id: chatId }),
                headers: { "Content-Type": "application/json" }
            })
            .then(r => r.json())
            .then(() => {
                if (chatId === currentChatId) {
                    startNewChat();
                }
                loadChatHistory();
            });
        }

        function renameChat(event, chatId) {
            event.stopPropagation();

            const newTitle = prompt("Novo título da conversa:");
            if (!newTitle) return;

            fetch("/api/rename_chat", {
                method: "POST",
                body: JSON.stringify({ chat_id: chatId, title: newTitle }),
                headers: { "Content-Type": "application/json" }
            })
            .then(r => r.json())
            .then(() => {
                loadChatHistory();
            });
        }

        function formatDate(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));

            if (days === 0) return "Hoje";
            if (days === 1) return "Ontem";
            if (days < 7) return `${days} dias atrás`;

            return date.toLocaleDateString('pt-BR');
        }

        // Salvar antes de fechar a página
        window.addEventListener("beforeunload", () => {
            if (messageCount > 0) {
                saveChat(true);
            }
        });


//        input.addEventListener("input", function() {
//            this.style.height = "22px";
//            this.style.height = Math.min(this.scrollHeight, 200) + "px";
//        });