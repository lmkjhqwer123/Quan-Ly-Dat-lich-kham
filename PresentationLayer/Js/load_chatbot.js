// Auto-load chatbot widget on all pages
function loadChatbot() {
    // Check if chatbot already exists
    if (document.getElementById('chatbot-widget')) {
        initializeChatbot();
        return;
    }

    // Try to find existing container or create new one
    let chatbotContainer = document.getElementById('chatbot-container');
    
    if (!chatbotContainer) {
        chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'chatbot-container';
        document.body.appendChild(chatbotContainer);
    }
    
    // Fetch and insert chatbot HTML
    fetch('/GUI/components/chatbot.html')
        .then(response => response.text())
        .then(html => {
            chatbotContainer.innerHTML = html;
            
            // Initialize chatbot functionality after DOM update
            setTimeout(() => {
                initializeChatbot();
            }, 50);
        })
        .catch(error => console.error('Error loading chatbot:', error));
}

// Run when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadChatbot);
} else {
    loadChatbot();
}

// Chatbot initialization function
function initializeChatbot() {
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotWindow = document.getElementById('chatbot-window');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotMessages = document.getElementById('chatbot-messages');

    if (!chatbotToggle) return; // Exit if chatbot elements not found

    // API Configuration
    const API_BASE = 'http://localhost:8000/api/chatbot';
    let conversationId = null;
    let isLoading = false;

    // Toggle chatbot window
    chatbotToggle.addEventListener('click', () => {
        chatbotWindow.classList.toggle('hidden');
        
        // Initialize conversation on first open
        if (!conversationId && chatbotWindow.classList.contains('hidden') === false) {
            createNewConversation();
        }
    });

    // Handle form submission
    chatbotForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatbotInput.value.trim();

        if (message && !isLoading) {
            // Add user message
            addMessage(message, 'user');
            chatbotInput.value = '';
            
            // Send to API
            await sendMessage(message);
        }
    });

    // Allow Enter to send
    chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isLoading) {
            chatbotForm.dispatchEvent(new Event('submit'));
        }
    });

    // Create new conversation
    async function createNewConversation() {
        try {
            const response = await fetch(`${API_BASE}/new-conversation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                conversationId = data.conversation_id;
                console.log('Conversation created:', conversationId);
            }
        } catch (error) {
            console.error('Error creating conversation:', error);
        }
    }

    // Send message to API
    async function sendMessage(message) {
        if (!conversationId) {
            await createNewConversation();
        }

        isLoading = true;
        
        try {
            const response = await fetch(`${API_BASE}/send-message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    message: message
                })
            });

            if (response.ok) {
                const data = await response.json();
                // Add bot response with booking data if available
                if (data.response) {
                    addMessage(data.response, 'bot', data.booking_data);
                }
            } else {
                addMessage('Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.', 'bot');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage('Kết nối bị lỗi. Vui lòng kiểm tra kết nối internet.', 'bot');
        } finally {
            isLoading = false;
        }
    }

    // Add message to chat
    function addMessage(text, sender, bookingData = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex gap-3 ${sender === 'user' ? 'justify-end' : ''}`;

        if (sender === 'bot') {
            let messageHTML = `
                <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-robot text-sm"></i>
                </div>
                <div class="bg-white rounded-lg rounded-tl-none p-3 shadow-sm max-w-xs">
                    <p class="text-gray-800 text-sm">${text}</p>
            `;
            
            // Thêm button "Đặt lịch" nếu có booking data
            if (bookingData && bookingData.specialty && bookingData.doctor && bookingData.date && bookingData.time) {
                console.log('🎯 [BOOKING] Showing booking button with data:', bookingData);
                messageHTML += `
                    <button class="mt-2 px-3 py-1 bg-blue-600 text-white text-xs rounded-md hover:bg-blue-700 transition book-appointment-btn" 
                        data-specialty-id="${bookingData.specialty_id || ''}" 
                        data-doctor-id="${bookingData.doctor_id || ''}" 
                        data-specialty="${encodeURIComponent(bookingData.specialty)}" 
                        data-doctor="${encodeURIComponent(bookingData.doctor)}" 
                        data-date="${bookingData.date}" 
                        data-time="${encodeURIComponent(bookingData.time)}">
                        📅 Đặt lịch ngay
                    </button>
                `;
            } else {
                console.log('❌ [BOOKING] No booking data or incomplete:', bookingData);
            }
            
            messageHTML += `
                    <span class="text-xs text-gray-400 mt-1 block">Umbrella mini bot</span>
                </div>
            `;
            messageDiv.innerHTML = messageHTML;
        } else {
            messageDiv.innerHTML = `
                <div class="bg-blue-600 text-white rounded-lg rounded-tr-none p-3 shadow-sm max-w-xs">
                    <p class="text-sm">${text}</p>
                </div>
            `;
        }

        chatbotMessages.appendChild(messageDiv);
        
        // Attach event listener to booking button
        if (bookingData && bookingData.specialty && bookingData.doctor) {
            const bookBtn = messageDiv.querySelector('.book-appointment-btn');
            if (bookBtn) {
                bookBtn.addEventListener('click', () => {
                    console.log('🖱️ [BOOKING] Button clicked, filling form with:', {
                        specialtyId: bookingData.specialty_id,
                        doctorId: bookingData.doctor_id,
                        date: bookingData.date,
                        time: bookingData.time
                    });
                    fillBookingForm(bookingData.specialty_id, bookingData.doctor_id, bookingData.date, bookingData.time);
                });
            }
        }
        
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
}

// Function to fill booking form from chatbot
function fillBookingForm(specialtyId, doctorId, date, timeSlot) {
    // Convert date format if needed (from YYYY-MM-DD to actual date)
    const dateObj = new Date(date);
    const formattedDate = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, '0')}-${String(dateObj.getDate()).padStart(2, '0')}`;
    
    // Navigate to appointments page if not already there
    if (!document.getElementById('booking-form')) {
        window.location.href = '/Page/appointments.html';
        // Store data in sessionStorage to fill form after page load
        sessionStorage.setItem('bookingData', JSON.stringify({
            specialty_id: specialtyId,
            doctor_id: doctorId,
            date: formattedDate,
            time: timeSlot
        }));
        return;
    }
    
    // Sequential filling with proper delays
    console.log('Starting form fill sequence...');
    
    // Step 1: Fill specialty dropdown
    console.log('Step 1: Selecting specialty (ID=' + specialtyId + ')...');
    const specialtySelect = document.getElementById('specialty');
    let specialtyFound = false;
    
    if (specialtySelect && specialtyId) {
        specialtySelect.value = specialtyId;
        specialtySelect.dispatchEvent(new Event('change'));
        specialtySelect.dispatchEvent(new Event('input'));
        specialtyFound = true;
        console.log('✓ Specialty selected (ID: ' + specialtyId + ')');
    }
    
    // Step 2: Fill doctor dropdown (wait for specialty change to load doctors)
    setTimeout(() => {
        console.log('Step 2: Selecting doctor (ID=' + doctorId + ')...');
        const doctorSelect = document.getElementById('doctor');
        let doctorFound = false;
        
        if (doctorSelect && doctorId) {
            // Wait for options to be populated
            const checkDoctorOptions = setInterval(() => {
                const docOptions = doctorSelect.querySelectorAll('option');
                if (docOptions.length > 1) {  // More than just placeholder
                    clearInterval(checkDoctorOptions);
                    doctorSelect.value = doctorId;
                    doctorSelect.dispatchEvent(new Event('change'));
                    doctorFound = true;
                    console.log('✓ Doctor selected (ID: ' + doctorId + ')');
                    
                    // Step 3: Select date on calendar
                    setTimeout(() => {
                        console.log('Step 3: Selecting date...');
                        const calendarDays = document.querySelectorAll('.calendar-day');
                        let dateFound = false;
                        
                        for (let day of calendarDays) {
                            const dayDate = day.getAttribute('data-date');
                            if (dayDate === formattedDate) {
                                day.click();
                                day.classList.add('selected');
                                dateFound = true;
                                console.log('✓ Date selected:', formattedDate);
                                break;
                            }
                        }
                        
                        // Step 4: Select time slot
                        setTimeout(() => {
                            console.log('Step 4: Selecting time slot (' + timeSlot + ')...');
                            const timeButtons = document.querySelectorAll('.time-slot-button');
                            let timeFound = false;
                            
                            for (let btn of timeButtons) {
                                if (btn.getAttribute('data-time') === timeSlot) {
                                    btn.click();
                                    btn.classList.add('bg-teal-500', 'text-white', 'hover:bg-teal-600');
                                    btn.classList.remove('bg-white', 'text-gray-700', 'hover:bg-gray-100');
                                    timeFound = true;
                                    console.log('✓ Time slot selected:', timeSlot);
                                    
                                    // Update hidden input
                                    document.getElementById('appointment-time').value = timeSlot;
                                    break;
                                }
                            }
                            
                            // Step 5: Scroll to form
                            setTimeout(() => {
                                console.log('Step 5: Scrolling to form...');
                                const bookingForm = document.getElementById('booking-form');
                                if (bookingForm) {
                                    bookingForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                    console.log('✓ Form visible');
                                }
                                console.log('✓ Form fill complete!');
                            }, 300);
                        }, 300);
                    }, 300);
                }
            }, 100);  // Check every 100ms
        }
    }, 500);  // Wait 500ms for specialty to load doctors
}

// Check if there's booking data from chatbot in sessionStorage
window.addEventListener('DOMContentLoaded', () => {
    const bookingDataStr = sessionStorage.getItem('bookingData');
    if (bookingDataStr) {
        const bookingData = JSON.parse(bookingDataStr);
        // Clear the session data
        sessionStorage.removeItem('bookingData');
        // Fill the form
        fillBookingForm(bookingData.specialty_id, bookingData.doctor_id, bookingData.date, bookingData.time);
    }
});
