// ====================================
// CHATBOT WIDGET - CONNECTED TO API
// ====================================
document.addEventListener('DOMContentLoaded', () => {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotMessages = document.getElementById('chatbot-messages');

    // State management
    let conversationId = null;
    let isLoading = false;

    // API Configuration
    const API_BASE_URL = '/api/chatbot'; // Adjust based on your API endpoint

    // ====================================
    // EVENT LISTENERS
    // ====================================

    // Toggle chatbot window
    chatbotToggle.addEventListener('click', () => {
        chatbotWindow.classList.toggle('hidden');
        // Start new conversation when opening
        if (!chatbotWindow.classList.contains('hidden') && !conversationId) {
            startNewConversation();
        }
    });

    // Handle form submission
    chatbotForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatbotInput.value.trim();

        if (message && !isLoading) {
            // Clear input
            chatbotInput.value = '';
            
            // Add user message to UI
            addMessage(message, 'user');
            
            // Send to backend
            sendMessageToBackend(message);
        }
    });

    // ====================================
    // CORE FUNCTIONS
    // ====================================

    /**
     * Start a new chat conversation
     */
    async function startNewConversation() {
        try {
            const response = await fetch(`${API_BASE_URL}/new-conversation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                console.error('Failed to start conversation');
                return;
            }

            const data = await response.json();
            conversationId = data.conversation_id;
            console.log('[Chatbot] Conversation started:', conversationId);
        } catch (error) {
            console.error('[Chatbot] Error starting conversation:', error);
        }
    }

    /**
     * Send user message to backend and get AI response
     */
    async function sendMessageToBackend(userMessage) {
        if (!conversationId) {
            // Create conversation if doesn't exist
            await startNewConversation();
        }

        isLoading = true;
        addLoadingIndicator();

        try {
            const response = await fetch(`${API_BASE_URL}/send-message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    message: userMessage
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Remove loading indicator
            removeLoadingIndicator();

            // Add bot response
            if (data.response) {
                addMessage(data.response, 'bot');
            }

            // Handle tool recommendations if any
            if (data.tool_used) {
                addToolInfo(data.tool_used, data.tool_response);
            }

        } catch (error) {
            console.error('[Chatbot] Error:', error);
            removeLoadingIndicator();
            addMessage('Xin lỗi, tôi gặp sự cố. Vui lòng thử lại sau.', 'bot');
        } finally {
            isLoading = false;
        }
    }

    /**
     * Add message to chat UI
     */
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex gap-3 ${sender === 'user' ? 'justify-end' : ''}`;

        if (sender === 'bot') {
            messageDiv.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-robot text-sm"></i>
                </div>
                <div class="bg-white rounded-lg rounded-tl-none p-3 shadow-sm max-w-xs">
                    <p class="text-gray-800 text-sm">${escapeHtml(text)}</p>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="bg-blue-600 text-white rounded-lg rounded-tr-none p-3 shadow-sm max-w-xs">
                    <p class="text-sm">${escapeHtml(text)}</p>
                </div>
            `;
        }

        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    /**
     * Add loading indicator while waiting for response
     */
    function addLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'chatbot-loading';
        loadingDiv.className = 'flex gap-3';
        loadingDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-sm"></i>
            </div>
            <div class="bg-white rounded-lg rounded-tl-none p-3 shadow-sm">
                <div class="flex gap-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
            </div>
        `;
        chatbotMessages.appendChild(loadingDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    /**
     * Remove loading indicator
     */
    function removeLoadingIndicator() {
        const loading = document.getElementById('chatbot-loading');
        if (loading) {
            loading.remove();
        }
    }

    /**
     * Display tool usage information
     */
    function addToolInfo(toolName, toolResponse) {
        const toolDiv = document.createElement('div');
        toolDiv.className = 'flex gap-3';
        toolDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center flex-shrink-0 text-xs">
                <i class="fas fa-wrench"></i>
            </div>
            <div class="bg-green-50 rounded-lg rounded-tl-none p-3 shadow-sm max-w-xs border border-green-200">
                <p class="text-green-800 text-xs font-semibold mb-1">🔧 Tool: ${escapeHtml(toolName)}</p>
                <p class="text-green-700 text-xs">${escapeHtml(toolResponse)}</p>
            </div>
        `;
        chatbotMessages.appendChild(toolDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
