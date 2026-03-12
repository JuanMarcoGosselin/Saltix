const breadcrumbs = {
        inicio: 'Inicio',
        recibos: 'Mis Recibos',
        historial: 'Historial de Pagos',
        asistencias: 'Mis Asistencias',
        perfil: 'Mi Perfil'
    };
    function showPage(id, btn) {
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        document.getElementById('page-' + id).classList.add('active');
        btn.classList.add('active');
        document.getElementById('breadcrumb').innerHTML = '<strong>' + breadcrumbs[id] + '</strong>';
        document.getElementById('sidebar').classList.remove('open');
    }

    const months = JSON.parse(document.getElementById('months-data').textContent || '[]');

    let currentMonthIdx = months.length ? Math.max(0, months.length - 1) : 0;
    let activeFaltaDay = null;
    let justifiedDays = new Set();

    function renderCalendar() {
        if (!months.length) {
            return;
        }
        const m = months[currentMonthIdx];
        document.getElementById('month-label').textContent = m.label;
        const firstDay = new Date(m.year, m.month, 1).getDay();
        const startOffset = firstDay === 0 ? 6 : firstDay - 1;
        const daysInMonth = new Date(m.year, m.month + 1, 0).getDate();
        const body = document.getElementById('cal-body');
        body.innerHTML = '';
        for (let i = 0; i < startOffset; i++) {
            const c = document.createElement('div');
            c.className = 'cal-cell empty';
            body.appendChild(c);
        }
        let asist = 0,
            faltas = 0,
            justif = 0,
            perm = 0;
        for (let d = 1; d <= daysInMonth; d++) {
            const dow = new Date(m.year, m.month, d).getDay();
            const isWe = dow === 0 || dow === 6;
            let status = m.data[d] || (isWe ? 'X' : null);
            if (justifiedDays.has(m.month + '-' + d))
                status = 'FJ';
            if (status === 'A')
                asist++;
            else if (status === 'F')
                faltas++;
            else if (status === 'FJ')
                justif++;
            else if (status === 'P')
                perm++;
            const cell = document.createElement('div');
            cell.className = 'cal-cell' + (isWe ? ' weekend' : '');
            const dn = document.createElement('div');
            dn.className = 'day-num';
            dn.textContent = d;
            cell.appendChild(dn);
            if (status) {
                const ds = document.createElement('div');
                const map = {
                    A: 'status-a',
                    F: 'status-f',
                    FJ: 'status-fj',
                    P: 'status-p',
                    V: 'status-v',
                    X: 'status-x'
                };
                const ico = {
                    A: '✓',
                    F: '✗',
                    FJ: '!',
                    P: 'P',
                    V: 'V',
                    X: '—'
                };
                ds.className = 'day-status ' + (map[status] || 'status-x');
                ds.textContent = ico[status] || '?';
                cell.appendChild(ds);
                if (status === 'F') {
                    cell.classList.add('has-falta');
                    const btn = document.createElement('button');
                    btn.className = 'btn-j-cell';
                    btn.textContent = 'Justificar';
                    btn.onclick = (e) => {
                        e.stopPropagation();
                        openModal(d, m.label, m.month);
                    };
                    cell.appendChild(btn);
                    cell.onclick = () => openModal(d, m.label, m.month);
                }
            }
            body.appendChild(cell);
        }
        document.getElementById('stat-asist').textContent = asist;
        document.getElementById('stat-faltas').textContent = faltas;
        document.getElementById('stat-justif').textContent = justif;
        document.getElementById('stat-perm').textContent = perm;
        renderFaltasTable(m);
    }

    function renderFaltasTable(m) {
        const tbody = document.getElementById('faltas-tbody');
        tbody.innerHTML = '';
        const daysInMonth = new Date(m.year, m.month + 1, 0).getDate();
        const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
        const meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
        let count = 0;
        for (let d = 1; d <= daysInMonth; d++) {
            if (m.data[d] === 'F' && !justifiedDays.has(m.month + '-' + d)) {
                count++;
                const dow = new Date(m.year, m.month, d).getDay();
                const tr = document.createElement('tr');
                tr.innerHTML = `<td style="padding:.85rem 1.5rem;font-size:.85rem;border-bottom:1px solid var(--gray-100)">${d} de ${meses[m.month]} de ${m.year}</td><td style="padding:.85rem 1.5rem;font-size:.85rem;border-bottom:1px solid var(--gray-100)">${dias[dow]}</td><td style="padding:.85rem 1.5rem;font-size:.85rem;border-bottom:1px solid var(--gray-100)"><span style="display:inline-block;padding:.18rem .65rem;border-radius:999px;font-size:.7rem;font-weight:700;background:#fdecea;color:#c0392b">Sin justificar</span></td><td style="padding:.85rem 1.5rem;font-size:.85rem;border-bottom:1px solid var(--gray-100)"><button onclick="openModal(${d},'${m.label}',${m.month})" style="background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border:none;border-radius:8px;padding:.4rem 1rem;font-family:'Plus Jakarta Sans',sans-serif;font-size:.78rem;font-weight:600;cursor:pointer">Justificar</button></td>`;
                tbody.appendChild(tr);
            }
        }
        if (count === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td colspan="4" style="padding:1.5rem;text-align:center;font-size:.85rem;color:var(--gray-400)">✅ Sin faltas pendientes de justificación</td>`;
            tbody.appendChild(tr);
        }
        document.getElementById('faltas-count').textContent = count > 0 ? count + ' pendiente' + (count > 1 ? 's' : '') : 'Sin pendientes';
    }

    function changeMonth(dir) {
        currentMonthIdx = Math.max(0, Math.min(months.length - 1, currentMonthIdx + dir));
        renderCalendar();
    }

    function openModal(day, monthLabel, monthIdx) {
        activeFaltaDay = {
            day,
            monthIdx
        };
        const meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
        const m = months[monthIdx];
        const dow = new Date(m.year, m.month, day).getDay();
        const dias = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
        document.getElementById('modal-fecha-label').textContent = `${dias[dow]} ${day} de ${meses[m.month]} de ${m.year}`;
        document.getElementById('motivo-select').value = '';
        document.getElementById('motivo-desc').value = '';
        document.getElementById('file-label').innerHTML = '<input type="file" id="file-input" accept=".pdf,.jpg,.png" onchange="handleFile(this)">📎 Adjunta un comprobante (PDF, JPG, PNG)';
        document.getElementById('modal-overlay').classList.add('open');
    }

    function closeModal(e) {
        if (e.target === document.getElementById('modal-overlay'))
            closeModalDirect();
    }
    function closeModalDirect() {
        document.getElementById('modal-overlay').classList.remove('open');
        activeFaltaDay = null;
    }

    function handleFile(input) {
        if (input.files.length > 0) {
            document.getElementById('file-label').innerHTML = `<input type="file" id="file-input" accept=".pdf,.jpg,.png" onchange="handleFile(this)">✅ <strong>${input.files[0].name}</strong> adjunto`;
        }
    }

    function submitJustificacion() {
        const motivo = document.getElementById('motivo-select').value;
        if (!motivo) {
            document.getElementById('motivo-select').style.borderColor = 'var(--red)';
            document.getElementById('motivo-select').focus();
            return;
        }
        document.getElementById('motivo-select').style.borderColor = '';
        if (activeFaltaDay)
            justifiedDays.add(activeFaltaDay.monthIdx + '-' + activeFaltaDay.day);
        closeModalDirect();
        renderCalendar();
        showToast('✅ Justificación enviada correctamente');
    }

    function showToast(msg) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 3500);
    }

    renderCalendar();
