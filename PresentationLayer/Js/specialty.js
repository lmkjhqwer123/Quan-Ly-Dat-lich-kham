document.addEventListener('DOMContentLoaded', function() {
    fetchSpecialties();

    async function fetchSpecialties() {
        try {
            const response = await fetch('/api/specialties');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const specialties = await response.json();
            populateSpecialtyTable(specialties);
        } catch (error) {
            console.error('Error fetching specialties:', error);
            // Optionally display an error message to the user
        }
    }

    function populateSpecialtyTable(specialties) {
        const tableBody = document.getElementById('specialty-table-body');
        if (!tableBody) {
            console.error('Specialty table body not found');
            return;
        }
        tableBody.innerHTML = ''; // Clear existing sample data

        specialties.forEach(specialty => {
            const row = `
                <tr class="border-b border-gray-200 hover:bg-gray-50">
                    <td class="py-4 px-6 font-medium">${specialty.SpecialtyId}</td>
                    <td class="py-4 px-6">
                        <div class="flex items-center space-x-3">
                            <span class="font-medium">${specialty.Name}</span>
                        </div>
                    </td>
                    <td class="py-4 px-6 space-x-2">
                        <button class="btn-action btn-edit">Sửa</button>
                        <button class="btn-action btn-delete">Xóa</button>
                    </td>
                </tr>
            `;
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    }
});