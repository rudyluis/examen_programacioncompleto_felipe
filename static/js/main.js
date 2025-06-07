document.addEventListener('DOMContentLoaded', function () {
    const regionFilter = document.getElementById('regionFilter');
    const yearFilter = document.getElementById('yearFilter');
    const cancerTypeFilter = document.getElementById('cancerTypeFilter');
    const genderFilter = document.getElementById('genderFilter');
    const cancerDataBody = document.getElementById('cancerDataBody');

    if (!regionFilter || !yearFilter || !cancerTypeFilter || !genderFilter || !cancerDataBody) {
        console.error('Uno o más elementos no existen en el DOM.');
        return;
    }

    fetch('/api/filtros')
        .then(response => response.json())
        .then(data => {
            data.regions.forEach(region => {
                const option = document.createElement('option');
                option.value = region;
                option.textContent = region;
                regionFilter.appendChild(option);
            });
            data.years.forEach(year => {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                yearFilter.appendChild(option);
            });
            data.cancer_types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                cancerTypeFilter.appendChild(option);
            });
            data.genders.forEach(gender => {
                const option = document.createElement('option');
                option.value = gender;
                option.textContent = gender;
                genderFilter.appendChild(option);
            });

            loadCancerData();
        })
        .catch(error => console.error('Error al cargar filtros:', error));

    regionFilter.addEventListener('change', loadCancerData);
    yearFilter.addEventListener('change', loadCancerData);
    cancerTypeFilter.addEventListener('change', loadCancerData);
    genderFilter.addEventListener('change', loadCancerData);

    function loadCancerData() {
        const params = new URLSearchParams({
            region: regionFilter.value,
            year: yearFilter.value,
            cancer_type: cancerTypeFilter.value,
            gender: genderFilter.value
        });

        fetch(`/api/cancer_data?${params}`)
            .then(response => response.json())
            .then(data => {
                cancerDataBody.innerHTML = '';
                if (data.length === 0) {
                    cancerDataBody.innerHTML = '<tr><td colspan="15" class="text-center">No hay datos disponibles</td></tr>';
                    return;
                }

                data.forEach(record => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${record.patient_id || ''}</td>
                        <td>${record.age || ''}</td>
                        <td>${record.gender || ''}</td>
                        <td>${record.region || ''}</td>
                        <td>${record.year || ''}</td>
                        <td>${record.genetic_risk || ''}</td>
                        <td>${record.air_pollution || ''}</td>
                        <td>${record.alcohol_consumption || ''}</td>
                        <td>${record.smoking || ''}</td>
                        <td>${record.obesity_level || ''}</td>
                        <td>${record.cancer_type || ''}</td>
                        <td>${record.cancer_stage || ''}</td>
                        <td>${record.treatment_cost || ''}</td>
                        <td>${record.survival_years || ''}</td>
                        <td>${record.severity_score || ''}</td>
                    `;
                    cancerDataBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error al cargar los datos:', error);
                cancerDataBody.innerHTML = '<tr><td colspan="15" class="text-center">Error al cargar los datos</td></tr>';
            });
    }
});
