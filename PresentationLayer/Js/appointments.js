document.addEventListener('DOMContentLoaded', function () {
    const specialtySelect = document.getElementById('specialty');
    const doctorSelect = document.getElementById('doctor');

    // Function to fetch specialties and populate the dropdown
    function loadSpecialties() {
        fetch('http://127.0.0.1:8000/api/specialties/')
            .then(response => response.json())
            .then(data => {
                data.forEach(specialty => {
                    const option = document.createElement('option');
                    option.value = specialty.SpecialtyId;
                    option.textContent = specialty.Name;
                    specialtySelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading specialties:', error));
    }

    // Function to fetch doctors based on specialty
    function loadDoctors(specialtyId) {
        // Clear existing doctor options
        doctorSelect.innerHTML = '<option value="" disabled selected>Đang tải...</option>';
        doctorSelect.disabled = true;

        fetch(`http://127.0.0.1:8000/api/doctors/?sort_speciality=${specialtyId}`)
            .then(response => response.json())
            .then(data => {
                doctorSelect.innerHTML = '<option value="" disabled selected>Chọn bác sĩ</option>';
                data.forEach(doctor => {
                    const option = document.createElement('option');
                    option.value = doctor.DoctorId;
                    option.textContent = doctor.FullName;
                    doctorSelect.appendChild(option);
                });
                doctorSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error loading doctors:', error);
                doctorSelect.innerHTML = '<option value="" disabled selected>Lỗi khi tải bác sĩ</option>';
            });
    }

    // Event listener for specialty change
    specialtySelect.addEventListener('change', function () {
        const selectedSpecialtyId = this.value;
        if (selectedSpecialtyId) {
            loadDoctors(selectedSpecialtyId);
        } else {
            // Disable and reset doctor select if no specialty is chosen
            doctorSelect.innerHTML = '<option value="" disabled selected>Vui lòng chọn chuyên khoa trước</option>';
            doctorSelect.disabled = true;
        }
    });

    // Initial load of specialties
    loadSpecialties();

    // Function to load patient info
    function loadPatientInfo() {
        const accessToken = sessionStorage.getItem('accessToken');
        if (!accessToken) {
            console.error('Access token not found.');
            // Redirect to login or show an error
            return;
        }

        fetch('/api/patients/me', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch patient information');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('full-name').value = data.FullName;
            document.getElementById('phone').value = data.Phone;
            document.getElementById('email').value = data.Email;
        })
        .catch(error => {
            console.error('Error loading patient info:', error);
        });
    }

    // Load patient info on page load
    loadPatientInfo();
});
