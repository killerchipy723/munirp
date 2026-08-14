document.addEventListener("DOMContentLoaded", function () {
    // --- REFERENCIAS A ELEMENTOS DEL DOM ---
    const inputFechaNac = document.getElementById('fecha_nacimiento'); // Input oculto (YYYY-MM-DD)
    const inputFechaNacMask = document.getElementById('fecha_nacimiento_mask'); // Input visible (DD/MM/AAAA)
    const selectGenero = document.getElementById('genero');
    const selectCategoria = document.getElementById('categoria_id');
    const inputCircuitoId = document.getElementById('circuito_id');
    const formInscripcion = document.getElementById('form-inscripcion');

    let listaCategorias = [];

    // --- MÁSCARA Y MÁQUINA DE ESCRIBIR DE FECHA (DD/MM/AAAA -> YYYY-MM-DD) ---
    if (inputFechaNacMask && inputFechaNac) {
        inputFechaNacMask.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, ''); // Remueve todo lo que no sea número
            
            if (value.length > 8) value = value.slice(0, 8);

            // Agrega automáticamente las barras "/"
            let formatted = value;
            if (value.length > 2 && value.length <= 4) {
                formatted = value.slice(0, 2) + '/' + value.slice(2);
            } else if (value.length > 4) {
                formatted = value.slice(0, 2) + '/' + value.slice(2, 4) + '/' + value.slice(4);
            }

            e.target.value = formatted;

            // Cuando la fecha está completa (DD/MM/AAAA = 10 caracteres)
            if (formatted.length === 10) {
                const parts = formatted.split('/');
                const dia = parts[0];
                const mes = parts[1];
                const ano = parts[2];

                // Convertimos a YYYY-MM-DD para la API
                inputFechaNac.value = `${ano}-${mes}-${dia}`;
                
                // Disparamos el evento 'change' para consultar categorías en la API
                inputFechaNac.dispatchEvent(new Event('change', { bubbles: true }));
            } else {
                inputFechaNac.value = '';
            }
        });
    }

    // --- BÚSQUEDA Y VALIDACIÓN DE CATEGORÍAS ---
    function validarYBuscarCategorias() {
        if (!inputFechaNac || !selectGenero || !selectCategoria) return;

        const fecha = inputFechaNac.value;
        const genero = selectGenero.value;

        if (fecha && genero) {
            fetch('/api/obtener-categorias', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ fecha_nacimiento: fecha, genero: genero })
            })
            .then(response => response.json())
            .then(data => {
                listaCategorias = data.categorias;
                selectCategoria.innerHTML = '<option value="">Seleccione categoría...</option>';
                selectCategoria.disabled = false;
                
                listaCategorias.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat.categoria_id;
                    opt.setAttribute('data-circuito', cat.circuito_id);
                    opt.textContent = `${cat.categoria_nombre} (${cat.kilometros} KM)`;
                    selectCategoria.appendChild(opt);
                });
            })
            .catch(err => console.error("Error obteniendo categorías:", err));
        }
    }

    // --- EVENT LISTENERS ---
    if (selectCategoria) {
        selectCategoria.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            const circuitoId = selectedOption ? selectedOption.getAttribute('data-circuito') : '';
            if (inputCircuitoId) inputCircuitoId.value = circuitoId || '';
        });
    }

    if (inputFechaNac) inputFechaNac.addEventListener('change', validarYBuscarCategorias);
    if (selectGenero) selectGenero.addEventListener('change', validarYBuscarCategorias);

    if (formInscripcion) {
        formInscripcion.addEventListener('submit', function (e) {
            if (selectCategoria) selectCategoria.disabled = false;
            if (inputCircuitoId && !inputCircuitoId.value && selectCategoria) {
                const selectedOption = selectCategoria.options[selectCategoria.selectedIndex];
                const circuitoId = selectedOption ? selectedOption.getAttribute('data-circuito') : '';
                if (circuitoId) {
                    inputCircuitoId.value = circuitoId;
                }
            }
        });
    }

    // --- DETECCIÓN Y DESPLIEGUE DEL MODAL ---
    const flashData = document.getElementById('flash-success-data');
    if (flashData) {
        const nombre = flashData.getAttribute('data-nombre');
        const dni = flashData.getAttribute('data-dni');
        const categoria = flashData.getAttribute('data-categoria');
        const idInscrito = flashData.getAttribute('data-id');

        const elNombre = document.getElementById('resumenNombre');
        const elDni = document.getElementById('resumenDni');
        const elCat = document.getElementById('resumenCategoria');
        const elNum = document.getElementById('resumenNumero');
        const elFecha = document.getElementById('resumenFecha');

        if (elNombre) elNombre.innerText = nombre;
        if (elDni) elDni.innerText = dni;
        if (elCat) elCat.innerText = categoria;
        if (elNum) elNum.innerText = "#MTB-2026-" + idInscrito;
        if (elFecha) elFecha.innerText = new Date().toLocaleDateString('es-AR');

        const modalElement = document.getElementById('modalConfirmacion');
        if (modalElement && typeof bootstrap !== 'undefined') {
            const modalObj = new bootstrap.Modal(modalElement);
            modalObj.show();
        }
    }
});