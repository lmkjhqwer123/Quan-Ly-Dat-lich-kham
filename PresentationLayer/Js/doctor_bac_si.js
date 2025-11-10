// doctor_bac_si.js

if (typeof window.initDoctorBacSiPage === 'undefined') {
    window.initDoctorBacSiPage = function() {
        const doctorAvatar = document.getElementById('doctor-avatar');
        const doctorFullName = document.getElementById('doctor-full-name');
        const doctorEmail = document.getElementById('doctor-email');
        const doctorPhone = document.getElementById('doctor-phone');
        const doctorSpecialty = document.getElementById('doctor-specialty');
        const doctorQualifications = document.getElementById('doctor-qualifications');
        const doctorRole = document.getElementById('doctor-role');
        const editProfileBtn = document.getElementById('edit-profile-btn');

        // Edit Modal Elements
        const editProfileModal = document.getElementById('edit-profile-modal');
        const cancelEditBtn = document.getElementById('cancel-edit-btn');
        const saveProfileBtn = document.getElementById('save-profile-btn');
        const editDoctorForm = document.getElementById('edit-doctor-form');
        const editDoctorId = document.getElementById('edit-doctor-id');
        const editFullName = document.getElementById('edit-full-name');
        const editEmail = document.getElementById('edit-email');
        const editPhone = document.getElementById('edit-phone');
        const editSpecialty = document.getElementById('edit-specialty');
        const editQualifications = document.getElementById('edit-qualifications');

        let specialties = [];

        const fetchSpecialties = async () => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found for specialties.');
                    window.location.href = '/login.html';
                    return;
                }
                const response = await fetch('/api/admin/specialties/', { // Assuming this endpoint is accessible to doctors for dropdown
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch specialties.');
                specialties = await response.json();
                populateSpecialtyDropdown(editSpecialty);
            } catch (error) {
                console.error('Error fetching specialties:', error);
            }
        };

        const populateSpecialtyDropdown = (selectElement) => {
            selectElement.innerHTML = '<option value="" disabled selected>Chọn chuyên khoa</option>';
            specialties.forEach(s => {
                const option = document.createElement('option');
                option.value = s.SpecialtyId;
                option.textContent = s.SpecialtyName;
                selectElement.appendChild(option);
            });
        };

        const fetchDoctorProfile = async () => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found.');
                    window.location.href = '/login.html';
                    return;
                }

                const response = await fetch('/api/doctor/profile', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => null); // Attempt to parse JSON, but don't fail if it's not JSON
                    console.error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}, errorData:`, errorData);
                    throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
                }

                const doctor = await response.json();
                displayDoctorProfile(doctor);

            } catch (error) {
                console.error('Error fetching doctor profile:', error);
                document.getElementById('doctor-profile-content').innerHTML = `<p class="text-center text-red-500">Lỗi khi tải thông tin cá nhân. Vui lòng thử lại.</p>`;
            }
        };

        const displayDoctorProfile = (doctor) => {
            doctorAvatar.src = doctor.Avatar || 'https://via.placeholder.com/150';
            doctorFullName.textContent = doctor.FullName;
            doctorEmail.textContent = doctor.Email;
            doctorPhone.textContent = doctor.Phone;
            doctorSpecialty.textContent = doctor.SpecialtyName || 'N/A';
            doctorQualifications.textContent = doctor.Qualifications || 'N/A';
            doctorRole.textContent = doctor.Role || 'Bác sĩ';

            // Populate edit modal fields
            editDoctorId.value = doctor.DoctorId;
            editFullName.value = doctor.FullName;
            editEmail.value = doctor.Email;
            editPhone.value = doctor.Phone;
            editQualifications.value = doctor.Qualifications;
            if (doctor.SpecialtyId) {
                editSpecialty.value = doctor.SpecialtyId;
            }
        };

        const handleEditProfile = async (event) => {
            event.preventDefault();
            const token = sessionStorage.getItem('accessToken');

            const updatedDoctorData = {
                FullName: editFullName.value,
                Phone: editPhone.value,
                SpecialtyId: parseInt(editSpecialty.value),
                Qualifications: editQualifications.value,
            };

            try {
                const response = await fetch(`/api/doctor/profile`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updatedDoctorData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Cập nhật thông tin thất bại.');
                }

                editProfileModal.classList.add('hidden');
                fetchDoctorProfile(); // Refresh profile display
                alert('Thông tin cá nhân đã được cập nhật thành công!');

            } catch (error) {
                console.error('Error updating doctor profile:', error);
                alert(error.message);
            }
        };

        // Event Listeners
        editProfileBtn.addEventListener('click', () => {
            editProfileModal.classList.remove('hidden');
        });

        cancelEditBtn.addEventListener('click', () => {
            editProfileModal.classList.add('hidden');
        });

        saveProfileBtn.addEventListener('click', handleEditProfile);

        // Initial fetch
        fetchSpecialties().then(fetchDoctorProfile);
    };
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initDoctorBacSiPage);
} else {
    window.initDoctorBacSiPage();
}
