const breadcrumbs={inicio:'Inicio',empleados:'Empleados',usuarios:'Usuarios',departamentos:'Planteles y Departamentos',configuracion:'Configuracion'};
const PAGE_STORAGE_KEY = 'admin_active_page';

function getNavButtons(){
  return Array.from(document.querySelectorAll('.nav-item'));
}

function getPageFromButton(btn){
  if (!btn) return '';
  const dataPage = btn.dataset.page;
  if (dataPage) return dataPage;
  const onClick = btn.getAttribute('onclick') || '';
  const match = onClick.match(/showPage\('([^']+)'\)/);
  return match ? match[1] : '';
}

function findNavButton(pageId){
  return getNavButtons().find(btn => getPageFromButton(btn) === pageId);
}

function saveActivePage(pageId){
  if (!pageId) return;
  try { localStorage.setItem(PAGE_STORAGE_KEY, pageId); } catch (e) {}
}

function restoreActivePage(){
  let pageId = '';
  try { pageId = localStorage.getItem(PAGE_STORAGE_KEY) || ''; } catch (e) {}
  if (!pageId || !document.getElementById('page-' + pageId)) {
    const defaultBtn = getNavButtons().find(btn => btn.classList.contains('active'));
    pageId = getPageFromButton(defaultBtn) || 'inicio';
  }
  const btn = findNavButton(pageId);
  showPage(pageId, btn || null);
}

function showPage(id,btn){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.getElementById('page-'+id).classList.add('active');
  if(btn)btn.classList.add('active');
  document.getElementById('breadcrumb').innerHTML='<strong>'+breadcrumbs[id]+'</strong>';
  document.getElementById('sidebar').classList.remove('open');
  saveActivePage(id);
}

const empleados = JSON.parse(document.getElementById('empleados-data').textContent || '[]');
const plantelesData = JSON.parse(document.getElementById('planteles-data').textContent || '[]');
const deptsByPlantel = JSON.parse(document.getElementById('depts-by-plantel').textContent || '{}');
const horariosByUser = JSON.parse(document.getElementById('horarios-by-user').textContent || '{}');
const jefesData = JSON.parse(document.getElementById('jefes-data').textContent || '[]');
const deptIndex = {};

function buildDeptIndex(){
  Object.keys(deptIndex).forEach(k => delete deptIndex[k]);
  plantelesData.forEach(p => {
    (p.depts || []).forEach(d => {
      deptIndex[String(d.id)] = {
        id: d.id,
        nombre: d.nombre,
        descripcion: d.descripcion || '',
        activo: d.activo,
        plantel_id: p.id,
        plantel_nombre: p.nombre,
      };
    });
  });
}

function renderPlanteles(){
  const container = document.getElementById('planteles-container');
  container.innerHTML = '';
  if (!plantelesData.length) {
    container.innerHTML = '<div style="text-align:center;color:var(--gray-400);padding:1.5rem;">Sin planteles registrados.</div>';
    return;
  }
  plantelesData.forEach(p => {
    const block = document.createElement('div');
    block.className = 'plantel-block';
    block.innerHTML = `
      <div class="plantel-header" onclick="togglePlantel('depts-${p.id}', this)">
        <div class="plantel-header-left">
          <div class="plantel-icon" style="background:var(--gray-100)">${p.icon}</div>
          <div>
            <div class="plantel-name">${p.nombre}</div>
            <div class="plantel-meta">${p.empleados} empleados &#x00B7; ${p.depts.length} departamentos &#x00B7; Responsable: ${p.jefe}</div>
          </div>
        </div>
        <div class="plantel-actions">
          <button class="btn-outline btn-sm" onclick="event.stopPropagation(); openModalPlantelEdit('${p.id}')">Editar</button>
          <button class="btn-outline btn-sm" onclick="event.stopPropagation(); openModalDeptCreate('${p.id}')">+ Dept</button>
          <span class="plantel-toggle-icon open" id="arrow-${p.id}">&#x25BC;</span>
        </div>
      </div>
      <div class="depts-grid" id="depts-${p.id}">
        ${p.depts.map(d => `
          <div class="card" style="position:relative;overflow:hidden;padding-top:1.6rem;">
            <div class="card-bar ${p.color}"></div>
            <div class="dept-card-top">
              <div style="font-size:.8rem;font-weight:700;color:var(--gray-400);margin-bottom:.2rem;">${p.nombre}</div>
              <button class="btn-outline btn-sm" onclick="openModalDeptEdit('${p.id}','${d.id}')">Editar</button>
            </div>
            <div style="font-weight:800;font-size:.9rem;margin-bottom:.2rem;">${d.nombre}</div>
            <div style="font-size:.75rem;color:var(--gray-400);margin-bottom:.5rem;">${d.empleados} empleados</div>
            <div class="progress-wrap">
              <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${d.prog}%"></div></div>
              <div class="progress-label"><span>Nomina</span><span>${d.prog === 0 ? 'Pendiente' : d.prog+'%'}</span></div>
            </div>
            <div class="dept-status ${d.activo ? 'dept-active' : 'dept-inactive'}">${d.activo ? 'Activo' : 'Inactivo'}</div>
          </div>`).join('')}
      </div>`;
    container.appendChild(block);
  });
}

function togglePlantel(id){
  const el = document.getElementById(id);
  const arrow = document.getElementById('arrow-' + id.replace('depts-',''));
  const isOpen = el.style.display !== 'none';
  el.style.display = isOpen ? 'none' : 'grid';
  if (arrow) arrow.classList.toggle('open', !isOpen);
}

let empFilter='todos', empSearch='';

function renderEmpleados(){
  const tbody=document.getElementById('emp-tbody');
  tbody.innerHTML='';
  const filtered=empleados.filter(e=>{
    const mf=empFilter==='todos'||(e.estado===empFilter);
    const ms=empSearch===''||e.nombre.toLowerCase().includes(empSearch.toLowerCase())||e.dept.toLowerCase().includes(empSearch.toLowerCase())||e.plantel.toLowerCase().includes(empSearch.toLowerCase());
    return mf&&ms;
  });
  if(!filtered.length){tbody.innerHTML='<tr><td colspan="8" style="padding:1.5rem;text-align:center;font-size:.85rem;color:var(--gray-400)">Sin resultados</td></tr>';return;}
  filtered.forEach(e=>{
    const pill=e.estado==='activo'?'<span class="pill pill-green">Activo</span>':'<span class="pill pill-gray">Baja</span>';
    const tr=document.createElement('tr');
    tr.innerHTML=`<td style="font-size:.8rem;color:var(--gray-400)">${e.id}</td><td>${e.nombre}</td><td><span class="pill pill-blue" style="font-size:.7rem;">${e.plantel}</span></td><td>${e.dept}</td><td>${e.puesto}</td><td>${e.salario}</td><td>${pill}</td><td style="color:var(--gray-400)">�</td>`;
    tbody.appendChild(tr);
  });
}
function filterEmpleados(f,btn){empFilter=f;document.querySelectorAll('#emp-tabs .tab-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');renderEmpleados();}
function searchEmpleados(val){empSearch=val;renderEmpleados();}

function searchUsuarios(val){
  const tbody = document.getElementById('usuarios-tbody');
  if (!tbody) return;
  const term = (val || '').trim().toLowerCase();
  const rows = Array.from(tbody.querySelectorAll('tr[data-search]'));
  let any = false;
  rows.forEach(row => {
    const match = !term || (row.dataset.search || '').includes(term);
    row.style.display = match ? '' : 'none';
    if (match) any = true;
  });
  let emptyRow = tbody.querySelector('tr.usuarios-empty');
  if (!rows.length) return;
  if (!any) {
    if (!emptyRow) {
      emptyRow = document.createElement('tr');
      emptyRow.className = 'usuarios-empty';
      emptyRow.innerHTML = '<td colspan="7" style="text-align:center;color:var(--gray-400);padding:1.25rem;">Sin resultados.</td>';
      tbody.appendChild(emptyRow);
    }
  } else if (emptyRow) {
    emptyRow.remove();
  }
}

function openModalUsuario(){
  const form = document.getElementById('user-form');
  form.action = form.dataset.createUrl;
  document.getElementById('modal-usr-title').textContent = 'Nuevo usuario';
  document.getElementById('user-id').value = '';
  document.getElementById('usr-email').value = '';
  document.getElementById('usr-nombre').value = '';
  document.getElementById('usr-apellido').value = '';
  document.getElementById('usr-rol').value = '';
  document.getElementById('usr-pass').value = '';
  document.getElementById('usr-pass2').value = '';
  Array.from(document.getElementById('usr-plantel').options).forEach(o=>o.selected=false);
  updateDeptsByPlantel('usr-plantel','usr-dept');
  Array.from(document.getElementById('usr-dept').options).forEach(o=>o.selected=false);
  clearProfesorFields();
  resetHorarioGrid();
  document.getElementById('horario-panel').style.display = 'none';
  setModalWidth(document.querySelector('#modal-usr .modal'), 1);
  document.getElementById('modal-usr').classList.add('open');
}

function openModalUsuarioEdit(btn){
  const form = document.getElementById('user-form');
  form.action = form.dataset.updateUrl;
  document.getElementById('modal-usr-title').textContent = 'Editar usuario';
  document.getElementById('user-id').value = btn.dataset.id || '';
  document.getElementById('usr-email').value = btn.dataset.email || '';
  document.getElementById('usr-nombre').value = btn.dataset.nombre || '';
  document.getElementById('usr-apellido').value = btn.dataset.apellido || '';
  document.getElementById('usr-rol').value = btn.dataset.rol || '';
  document.getElementById('usr-pass').value = '';
  document.getElementById('usr-pass2').value = '';
  const plantelSel = document.getElementById('usr-plantel');
  const planteles = (btn.dataset.planteles || '').split(',').filter(Boolean);
  Array.from(plantelSel.options).forEach(o=>o.selected = planteles.includes(o.value));
  updateDeptsByPlantel('usr-plantel','usr-dept');
  const deptIds = (btn.dataset.departamentos || '').split(',').filter(Boolean);
  Array.from(document.getElementById('usr-dept').options).forEach(o=>o.selected = deptIds.includes(o.value));

  resetHorarioGrid();
  fillProfesorFields(btn);
  const uid = btn.dataset.id;
  if (uid && horariosByUser[uid]) {
    applyHorarioFromRanges(horariosByUser[uid]);
  }
  document.getElementById('horario-panel').style.display = 'none';
  setModalWidth(document.querySelector('#modal-usr .modal'), 2);
  document.getElementById('modal-usr').classList.add('open');
}

function togglePlantelField(){
  const modal = document.querySelector('#modal-usr .modal');
  const role = document.getElementById('usr-rol').value;
  const prof = document.getElementById('profesor-fields');
  const jefe = document.getElementById('jefatura-panel');
  const plantelWrap = document.getElementById('usr-plantel-wrap');
  const deptWrap = document.getElementById('usr-dept-wrap');
  const right = document.getElementById('role-panels');
  const split = document.getElementById('user-modal-split');
  const horarioPanel = document.getElementById('horario-panel');
  const showProf = role === 'profesor';
  const showJefe = role === 'jefatura';
  setProfesorRequired(showProf);
  plantelWrap.style.display = showProf ? 'block' : 'none';
  deptWrap.style.display = showProf ? 'block' : 'none';
  prof.style.display = showProf ? 'block' : 'none';
  if (!showProf) horarioPanel.style.display = 'none';
  jefe.style.display = showJefe ? 'block' : 'none';
  if (!showProf) resetHorarioGrid();
  const hasRight = showProf || showJefe;
  right.style.display = hasRight ? 'block' : 'none';
  split.classList.toggle('single-column', !hasRight);
  setModalWidth(modal, hasRight ? 2 : 1);
}

function setProfesorRequired(required){
  const ids = [
    'prof-salario','prof-contrato','prof-rfc','prof-curp','prof-telefono','prof-direccion','prof-fecha'
  ];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.required = required;
  });
  const plantel = document.getElementById('usr-plantel');
  const dept = document.getElementById('usr-dept');
  if (plantel) plantel.required = required;
  if (dept) dept.required = required;
}

function clearProfesorFields(){
  document.getElementById('prof-salario').value = '';
  document.getElementById('prof-contrato').value = '';
  document.getElementById('prof-rfc').value = '';
  document.getElementById('prof-curp').value = '';
  document.getElementById('prof-telefono').value = '';
  document.getElementById('prof-direccion').value = '';
  document.getElementById('prof-fecha').value = '';
  clearJefaturaFields();
  document.getElementById('usr-plantel-wrap').style.display = 'none';
  document.getElementById('usr-dept-wrap').style.display = 'none';
  togglePlantelField();
}

function fillProfesorFields(btn){
  document.getElementById('prof-salario').value = btn.dataset.salario || '';
  document.getElementById('prof-contrato').value = btn.dataset.tipoContrato || '';
  document.getElementById('prof-rfc').value = btn.dataset.rfc || '';
  document.getElementById('prof-curp').value = btn.dataset.curp || '';
  document.getElementById('prof-telefono').value = btn.dataset.telefono || '';
  document.getElementById('prof-direccion').value = btn.dataset.direccion || '';
  document.getElementById('prof-fecha').value = btn.dataset.fechaIngreso || '';
  fillJefaturaFields(btn);
  togglePlantelField();
}

function clearJefaturaFields(){
  document.getElementById('jef-plantel').value = '';
  document.getElementById('jef-depto').innerHTML = '<option value="">-- Selecciona plantel --</option>';
}

function fillJefaturaFields(btn){
  const plantelId = btn.dataset.jefPlantel || '';
  const deptId = btn.dataset.jefDept || '';
  document.getElementById('jef-plantel').value = plantelId;
  updateJefaturaDepts();
  document.getElementById('jef-depto').value = deptId;
}

function updateJefaturaDepts(){
  const plantelId = document.getElementById('jef-plantel').value;
  const deptSel = document.getElementById('jef-depto');
  if (!plantelId) {
    deptSel.innerHTML = '<option value="">-- Selecciona plantel --</option>';
    return;
  }
  const list = deptsByPlantel[plantelId] || [];
  deptSel.innerHTML = list.length
    ? list
        .slice()
        .sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''))
        .map(d => `<option value="${d.id}">${d.nombre}</option>`)
        .join('')
    : '<option value="">Sin departamentos disponibles</option>';
}

function toggleHorarioPanel(){
  const modal = document.querySelector('#modal-usr .modal');
  const horarioPanel = document.getElementById('horario-panel');
  const show = horarioPanel.style.display !== 'block';
  horarioPanel.style.display = show ? 'block' : 'none';
  const right = document.getElementById('role-panels');
  const hasRight = right.style.display === 'block';
  setModalWidth(modal, hasRight ? 2 : 1);
}

function setModalWidth(modal, cols){
  if (!modal) return;
  modal.classList.remove('cols-1','cols-2','cols-3');
  modal.classList.add(`cols-${cols}`);
}

function resetHorarioGrid(){
  document.querySelectorAll('.horario-slot').forEach(cb => cb.checked = false);
  const hidden = document.getElementById('horario-hidden');
  if (hidden) hidden.innerHTML = '';
}

function applyHorarioFromRanges(ranges){
  if (!Array.isArray(ranges)) return;
  const slots = document.querySelectorAll('.horario-slot');
  const slotMap = {};
  slots.forEach(cb => {
    const key = `${cb.dataset.day}-${cb.dataset.hour}`;
    slotMap[key] = cb;
  });
  ranges.forEach(r => {
    const day = r.dia;
    const inicio = (r.inicio || '').split(':');
    const fin = (r.fin || '').split(':');
    if (!day || inicio.length < 2 || fin.length < 2) return;
    let startHour = parseInt(inicio[0], 10);
    let endHour = parseInt(fin[0], 10);
    const endMin = parseInt(fin[1], 10);
    if (r.fin === '23:59') endHour = 24;
    for (let h = startHour; h < endHour; h++) {
      const key = `${day}-${h}`;
      if (slotMap[key]) slotMap[key].checked = true;
    }
  });
}

function buildHorarioHiddenInputs(){
  const hidden = document.getElementById('horario-hidden');
  if (!hidden) return;
  hidden.innerHTML = '';
  const slots = Array.from(document.querySelectorAll('.horario-slot:checked'));
  const byDay = {};
  slots.forEach(cb => {
    const day = cb.dataset.day;
    const hour = parseInt(cb.dataset.hour, 10);
    if (!byDay[day]) byDay[day] = [];
    byDay[day].push(hour);
  });

  const dayOrder = Array.from(document.querySelectorAll('.horario-grid thead th[data-day]')).map(th => th.dataset.day);
  dayOrder.forEach(day => {
    const hours = (byDay[day] || []).sort((a, b) => a - b);
    let i = 0;
    while (i < hours.length) {
      const start = hours[i];
      let end = start + 1;
      i++;
      while (i < hours.length && hours[i] === end) {
        end++;
        i++;
      }
      const startStr = `${String(start).padStart(2,'0')}:00`;
      const endStr = end >= 24 ? '23:59' : `${String(end).padStart(2,'0')}:00`;
      appendHorarioInput(`horario_${day}_inicio[]`, startStr);
      appendHorarioInput(`horario_${day}_fin[]`, endStr);
      appendHorarioInput(`horario_${day}_aula[]`, '');
      appendHorarioInput(`horario_${day}_clase_val[]`, '1');
    }
  });
}

function appendHorarioInput(name, value){
  const hidden = document.getElementById('horario-hidden');
  if (!hidden) return;
  const input = document.createElement('input');
  input.type = 'hidden';
  input.name = name;
  input.value = value;
  hidden.appendChild(input);
}

function getSelectedValues(sel){
  return Array.from(sel.selectedOptions).map(o=>o.value);
}

function updateDeptsByPlantel(plantelSelId, deptSelId){
  const plantelSel = document.getElementById(plantelSelId);
  const deptSel = document.getElementById(deptSelId);
  const selected = getSelectedValues(plantelSel);
  const prevSelected = getSelectedValues(deptSel);
  if (!selected.length) {
    deptSel.innerHTML = '<option value="">-- Selecciona plantel --</option>';
    return;
  }

  const optgroups = selected.map(pid => {
    const list = deptsByPlantel[pid] || [];
    const plantel = plantelesData.find(p => String(p.id) === String(pid));
    const label = plantel ? plantel.nombre : `Plantel ${pid}`;
    const options = list
      .slice()
      .sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''))
      .map(d => {
        const selectedAttr = prevSelected.includes(String(d.id)) ? ' selected' : '';
        return `<option value="${d.id}"${selectedAttr}>${d.nombre}</option>`;
      }).join('');
    return `<optgroup label="${label}">${options}</optgroup>`;
  });

  deptSel.innerHTML = optgroups.join('') || '<option value="">Sin departamentos disponibles</option>';
}

let modalDepts = [];
function openModalPlantel(){
  document.getElementById('modal-plantel').classList.add('open');
  document.getElementById('plantel-nombre').value = '';
  document.getElementById('plantel-dir').value = '';
  modalDepts = [];
  renderModalDepts();
}

function addDeptToModal(){
  const input=document.getElementById('nuevo-dept-input');
  const val=input.value.trim();
  if(!val) return;
  if (!modalDepts.includes(val)) modalDepts.push(val);
  input.value='';
  renderModalDepts();
}

function removeModalDept(i){
  modalDepts.splice(i,1);
  renderModalDepts();
}

function renderModalDepts(){
  const list=document.getElementById('depts-list');
  const hidden=document.getElementById('departamentos-csv');
  if(!modalDepts.length){
    list.innerHTML='<div style="text-align:center;font-size:.82rem;color:var(--gray-400);padding:1rem 0;">Sin departamentos agregados aun</div>';
    hidden.value = '';
    return;
  }
  hidden.value = modalDepts.join(',');
  list.innerHTML=modalDepts.map((d,i)=>`
    <div style="display:flex;align-items:center;justify-content:space-between;background:var(--gray-100);border-radius:9px;padding:.6rem 1rem;">
      <span style="font-size:.875rem;font-weight:500;color:var(--navy);">${d}</span>
      <button type="button" onclick="removeModalDept(${i})" style="background:none;border:none;color:#c0392b;font-size:.85rem;cursor:pointer;padding:.1rem .3rem;border-radius:5px;" title="Eliminar">&#x2715;</button>
    </div>`).join('');
}

function openModalPlantelEdit(id){
  const plantel = plantelesData.find(p => String(p.id) === String(id));
  if (!plantel) return;
  document.getElementById('plantel-edit-id').value = plantel.id;
  document.getElementById('plantel-edit-nombre').value = plantel.nombre || '';
  document.getElementById('plantel-edit-dir').value = plantel.dir || '';
  document.getElementById('plantel-edit-activo').checked = !!plantel.activo;
  document.getElementById('modal-plantel-edit').classList.add('open');
}

function openModalDeptCreate(plantelId){
  const form = document.getElementById('dept-form');
  form.action = form.dataset.createUrl;
  document.getElementById('dept-modal-title').textContent = 'Nuevo departamento';
  document.getElementById('dept-id').value = '';
  document.getElementById('dept-nombre').value = '';
  document.getElementById('dept-descripcion').value = '';
  document.getElementById('dept-activo').checked = true;
  document.getElementById('dept-plantel-id').value = plantelId;
  const plantel = plantelesData.find(p => String(p.id) === String(plantelId));
  document.getElementById('dept-plantel-label').textContent = plantel ? `Plantel: ${plantel.nombre}` : '';
  renderJefesOptions(plantelId, '');
  document.getElementById('dept-submit').textContent = 'Guardar departamento';
  document.getElementById('modal-dept').classList.add('open');
}

function openModalDeptEdit(plantelId, deptId){
  const form = document.getElementById('dept-form');
  form.action = form.dataset.updateUrl;
  const depto = deptIndex[String(deptId)];
  if (!depto) return;
  document.getElementById('dept-modal-title').textContent = 'Editar departamento';
  document.getElementById('dept-id').value = depto.id;
  document.getElementById('dept-nombre').value = depto.nombre || '';
  document.getElementById('dept-descripcion').value = depto.descripcion || '';
  document.getElementById('dept-activo').checked = !!depto.activo;
  document.getElementById('dept-plantel-id').value = plantelId;
  document.getElementById('dept-plantel-label').textContent = `Plantel: ${depto.plantel_nombre}`;
  renderJefesOptions(plantelId, String(depto.id));
  document.getElementById('dept-submit').textContent = 'Guardar cambios';
  document.getElementById('modal-dept').classList.add('open');
}

function renderJefesOptions(plantelId, deptId){
  const sel = document.getElementById('dept-jefe');
  const opts = jefesData.filter(j => {
    const assigned = j.dept_id ? String(j.dept_id) : '';
    const sameDept = deptId && assigned === String(deptId);
    const unassigned = !assigned;
    const samePlantel = j.plantel_id ? String(j.plantel_id) === String(plantelId) : true;
    return (unassigned || sameDept) && samePlantel;
  });
  sel.innerHTML = '<option value="">— Sin asignar —</option>' +
    opts.map(j => `<option value="${j.id}"${j.dept_id && String(j.dept_id) === String(deptId) ? ' selected' : ''}>${j.nombre}</option>`).join('');
}

function showToast(msg){
  const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),3500);
}

function deletePlantel(plantelId){
  const plantel = plantelesData.find(p => String(p.id) === String(plantelId));
  const nombre = plantel ? plantel.nombre : 'este plantel';
  const count = plantel ? plantel.depts.length : 0;
  const msg = count
    ? `¿Eliminar "${nombre}"? Se eliminarán ${count} departamento(s).`
    : `¿Eliminar "${nombre}"?`;
  if (!confirm(msg)) return;
  const form = document.getElementById('plantel-delete-form');
  document.getElementById('plantel-delete-id').value = plantelId;
  form.submit();
}

function deleteDepartamento(deptId){
  const depto = deptIndex[String(deptId)];
  const nombre = depto ? depto.nombre : 'este departamento';
  if (!confirm(`¿Eliminar "${nombre}"? Esta acción no se puede deshacer.`)) return;
  const form = document.getElementById('dept-delete-form');
  document.getElementById('dept-delete-id').value = deptId;
  form.submit();
}

function deletePlantelFromEdit(){
  const plantelId = document.getElementById('plantel-edit-id').value;
  if (!plantelId) return;
  deletePlantel(plantelId);
}

function deleteDepartamentoFromEdit(){
  const deptId = document.getElementById('dept-id').value;
  if (!deptId) return;
  deleteDepartamento(deptId);
}

renderEmpleados();
buildDeptIndex();
renderPlanteles();
updateDeptsByPlantel('usr-plantel','usr-dept');
restoreActivePage();

document.getElementById('user-form').addEventListener('submit', (e) => {
  const role = document.getElementById('usr-rol').value;
  if (role === 'profesor') {
    buildHorarioHiddenInputs();
  } else {
    const hidden = document.getElementById('horario-hidden');
    if (hidden) hidden.innerHTML = '';
  }
});

const notifBtn = document.getElementById('notif-btn');
const notifPanel = document.getElementById('notif-panel');
if (notifBtn && notifPanel) {
  const readAllUrl = notifPanel.dataset.readAllUrl;
  const readOneUrl = notifPanel.dataset.readOneUrl;
  const markAllBtn = document.getElementById('notif-mark-read');

  function getCsrfToken(){
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }

  function clearNotifDot(){
    const dot = notifBtn.querySelector('.notif-dot');
    if (dot) dot.remove();
  }

  async function postNotif(url, body){
    if (!url) return;
    await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCsrfToken()
      },
      body
    });
  }

  async function markAllRead(){
    await postNotif(readAllUrl, '');
    clearNotifDot();
    notifPanel.querySelectorAll('.notif-item').forEach(item => {
      item.classList.remove('notif-unread');
    });
  }

  notifBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    notifPanel.classList.toggle('open');
    if (notifPanel.classList.contains('open')) {
      markAllRead();
    }
  });
  document.addEventListener('click', (e) => {
    if (!notifPanel.contains(e.target) && !notifBtn.contains(e.target)) {
      notifPanel.classList.remove('open');
    }
  });

  if (markAllBtn) {
    markAllBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      markAllRead();
    });
  }

  notifPanel.querySelectorAll('.notif-dismiss').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const item = btn.closest('.notif-item');
      const id = item ? item.dataset.id : '';
      if (!id) return;
      await postNotif(readOneUrl, `notif_id=${encodeURIComponent(id)}`);
      item.remove();
      const remaining = notifPanel.querySelectorAll('.notif-item').length;
      if (!remaining) {
        const empty = document.createElement('div');
        empty.className = 'notif-empty';
        empty.textContent = 'Sin notificaciones recientes.';
        notifPanel.querySelector('.notif-list').appendChild(empty);
      }
      clearNotifDot();
    });
  });
}
