/* ══ NAVEGACIÓN ══ */
const breadcrumbs={inicio:'Inicio',empleados:'Empleados',usuarios:'Usuarios',departamentos:'Planteles y Departamentos',configuracion:'Configuración'};
function showPage(id,btn){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.getElementById('page-'+id).classList.add('active');
  if(btn)btn.classList.add('active');
  document.getElementById('breadcrumb').innerHTML='<strong>'+breadcrumbs[id]+'</strong>';
  document.getElementById('sidebar').classList.remove('open');
}

/* ══ DATOS ══ */
const deptsByPlantel = {
  norte:  ['Matemáticas','Ciencias','Humanidades'],
  centro: ['Administración','Sistemas','Arte y Diseño'],
  sur:    ['Educación Física','Idiomas'],
  todos:  []
};

const plantelesData = [
  { id:'norte',  nombre:'Plantel Norte',  icon:'🏫', color:'bar-blue',
    empleados:55, jefe:'María Alvarado', dir:'Av. Insurgentes Norte 1200, CDMX',
    depts:[
      {nombre:'Matemáticas', empleados:18, prog:82},
      {nombre:'Ciencias',    empleados:15, prog:100},
      {nombre:'Humanidades', empleados:22, prog:55},
    ]},
  { id:'centro', nombre:'Plantel Centro', icon:'🏛️', color:'bar-teal',
    empleados:37, jefe:'Rosa Fernández', dir:'Calle Madero 45, Centro Histórico, CDMX',
    depts:[
      {nombre:'Administración', empleados:12, prog:70},
      {nombre:'Sistemas',       empleados:10, prog:0},
      {nombre:'Arte y Diseño',  empleados:9,  prog:100},
    ]},
  { id:'sur',    nombre:'Plantel Sur',    icon:'🏢', color:'bar-orange',
    empleados:28, jefe:'Sin asignar', dir:'Calz. de Tlalpan 3800, CDMX',
    depts:[
      {nombre:'Educación Física', empleados:8,  prog:100},
      {nombre:'Idiomas',          empleados:14, prog:90},
    ]},
];

/* ══ RENDER PLANTELES ══ */
function renderPlanteles(){
  const container = document.getElementById('planteles-container');
  container.innerHTML = '';
  plantelesData.forEach(p => {
    const block = document.createElement('div');
    block.className = 'plantel-block';
    block.innerHTML = `
      <div class="plantel-header" onclick="togglePlantel('depts-${p.id}', this)">
        <div class="plantel-header-left">
          <div class="plantel-icon" style="background:var(--gray-100)">${p.icon}</div>
          <div>
            <div class="plantel-name">${p.nombre}</div>
            <div class="plantel-meta">${p.empleados} empleados · ${p.depts.length} departamentos · Responsable: ${p.jefe}</div>
          </div>
        </div>
        <div class="plantel-actions">
          <button class="btn-outline" style="padding:.3rem .8rem;font-size:.75rem;" onclick="event.stopPropagation();openModalPlantelEdit('${p.id}')">Editar</button>
          <button style="background:#fdecea;color:#c0392b;border:1px solid #f5c6c2;border-radius:7px;padding:.3rem .8rem;font-size:.75rem;cursor:pointer;" onclick="event.stopPropagation();showToast('🗑️ Plantel eliminado')">Eliminar</button>
          <span class="plantel-toggle-icon open" id="arrow-${p.id}">▼</span>
        </div>
      </div>
      <div class="depts-grid" id="depts-${p.id}">
        ${p.depts.map(d => `
          <div class="card" style="position:relative;overflow:hidden;padding-top:1.6rem;">
            <div class="card-bar ${p.color}"></div>
            <div style="font-size:.8rem;font-weight:700;color:var(--gray-400);margin-bottom:.2rem;">${p.nombre}</div>
            <div style="font-weight:800;font-size:.9rem;margin-bottom:.2rem;">${d.nombre}</div>
            <div style="font-size:.75rem;color:var(--gray-400);margin-bottom:.5rem;">${d.empleados} empleados</div>
            <div class="progress-wrap">
              <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${d.prog}%"></div></div>
              <div class="progress-label"><span>Nómina</span><span>${d.prog === 0 ? 'Pendiente' : d.prog+'%'}</span></div>
            </div>
            <div style="display:flex;gap:.4rem;margin-top:.75rem;">
              <button class="btn-outline" style="flex:1;padding:.35rem;font-size:.75rem;" onclick="showToast('⚙️ Editando ${d.nombre}')">Editar</button>
              <button style="flex:1;background:#fdecea;color:#c0392b;border:1px solid #f5c6c2;border-radius:7px;padding:.35rem;font-size:.75rem;cursor:pointer;" onclick="showToast('🗑️ Departamento eliminado')">Eliminar</button>
            </div>
          </div>`).join('')}
        <div class="card" style="border:2px dashed var(--gray-200);background:transparent;display:flex;align-items:center;justify-content:center;min-height:120px;cursor:pointer;transition:border-color .2s,background .2s;" onmouseover="this.style.borderColor='var(--accent)';this.style.background='#f4f9ff'" onmouseout="this.style.borderColor='var(--gray-200)';this.style.background='transparent'" onclick="showToast('➕ Agregar departamento a ${p.nombre}')">
          <div style="text-align:center;color:var(--gray-400);">
            <div style="font-size:1.4rem;">➕</div>
            <div style="font-size:.78rem;font-weight:600;margin-top:.35rem;">Nuevo depto.</div>
          </div>
        </div>
      </div>`;
    container.appendChild(block);
  });
}

function togglePlantel(id, header){
  const el = document.getElementById(id);
  const arrow = document.getElementById('arrow-' + id.replace('depts-',''));
  const isOpen = el.style.display !== 'none';
  el.style.display = isOpen ? 'none' : 'grid';
  arrow.classList.toggle('open', !isOpen);
}

/* ══ DATOS EMPLEADOS ══ */
const empleados=[
  {id:1,nombre:'Ana García',plantel:'Plantel Norte',dept:'Matemáticas',puesto:'Profesora TC',salario:'$18,500',estado:'activo'},
  {id:2,nombre:'Luis Morales',plantel:'Plantel Norte',dept:'Matemáticas',puesto:'Profesor TC',salario:'$18,500',estado:'activo'},
  {id:3,nombre:'Carmen Ruiz',plantel:'Plantel Norte',dept:'Matemáticas',puesto:'Asistente',salario:'$12,000',estado:'activo'},
  {id:4,nombre:'Pedro Soto',plantel:'Plantel Norte',dept:'Ciencias',puesto:'Profesor TC',salario:'$19,000',estado:'activo'},
  {id:5,nombre:'Rosa Méndez',plantel:'Plantel Norte',dept:'Humanidades',puesto:'Tutora',salario:'$10,500',estado:'activo'},
  {id:6,nombre:'Jorge Herrera',plantel:'Plantel Norte',dept:'Humanidades',puesto:'Profesor',salario:'$18,000',estado:'baja'},
  {id:7,nombre:'Iván Gosseline',plantel:'Plantel Norte',dept:'Matemáticas',puesto:'Profesor TC',salario:'$18,500',estado:'activo'},
  {id:8,nombre:'María Alvarado',plantel:'Plantel Centro',dept:'Administración',puesto:'Jefa de Dept.',salario:'$28,000',estado:'activo'},
  {id:9,nombre:'Roberto Vela',plantel:'Plantel Centro',dept:'Sistemas',puesto:'Técnico',salario:'$16,000',estado:'activo'},
  {id:10,nombre:'Sandra Cruz',plantel:'Plantel Sur',dept:'Idiomas',puesto:'Profesora TC',salario:'$17,500',estado:'baja'},
];
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
    tr.innerHTML=`<td style="font-size:.8rem;color:var(--gray-400)">${e.id}</td><td>${e.nombre}</td><td><span class="pill pill-blue" style="font-size:.7rem;">${e.plantel}</span></td><td>${e.dept}</td><td>${e.puesto}</td><td>${e.salario}</td><td>${pill}</td><td style="display:flex;gap:.4rem;padding:.85rem 1.5rem"><button class="btn-outline" style="padding:.3rem .7rem;font-size:.75rem;" onclick="openModalEmpleadoEdit('${e.nombre}')">Editar</button><button style="background:#fdecea;color:#c0392b;border:1px solid #f5c6c2;border-radius:7px;padding:.3rem .7rem;font-size:.75rem;cursor:pointer;" onclick="showToast('🗑️ Empleado eliminado')">Eliminar</button></td>`;
    tbody.appendChild(tr);
  });
}
function filterEmpleados(f,btn){empFilter=f;document.querySelectorAll('#emp-tabs .tab-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');renderEmpleados();}
function searchEmpleados(val){empSearch=val;renderEmpleados();}

/* ══ MODALES EMPLEADO ══ */
function openModalEmpleado(){
  document.getElementById('modal-emp-title').textContent='Nuevo empleado';
  document.getElementById('emp-plantel-sel').value='';
  document.getElementById('emp-dept-sel').innerHTML='<option value="">— Primero selecciona un plantel —</option>';
  document.getElementById('modal-emp').classList.add('open');
}
function openModalEmpleadoEdit(nombre){
  document.getElementById('modal-emp-title').textContent='Editar: '+nombre;
  document.getElementById('modal-emp').classList.add('open');
}

/* ══ MODAL USUARIO ══ */
function openModalUsuario(){
  document.getElementById('modal-usr-title').textContent='Nuevo usuario';
  document.getElementById('usr-username').value='';
  document.getElementById('usr-rol').value='';
  document.getElementById('usr-plantel').value='';
  document.getElementById('usr-dept').innerHTML='<option value="">— Primero selecciona un plantel —</option>';
  document.getElementById('usr-pass').value='';
  document.getElementById('usr-pass2').value='';
  document.getElementById('usr-email').value='';
  togglePlantelField();
  document.getElementById('modal-usr').classList.add('open');
}
function openModalUsuarioEdit(username, nombre, rol, plantel){
  document.getElementById('modal-usr-title').textContent='Editar: '+nombre;
  document.getElementById('usr-username').value=username;
  document.getElementById('usr-rol').value=rol;
  document.getElementById('usr-plantel').value=plantel;
  updateDeptsByPlantel('usr-plantel','usr-dept');
  togglePlantelField();
  document.getElementById('modal-usr').classList.add('open');
}
function togglePlantelField(){
  const rol=document.getElementById('usr-rol').value;
  const wrap=document.getElementById('usr-plantel-wrap');
  const dwrap=document.getElementById('usr-dept-wrap');
  // Admin no necesita plantel específico (tiene acceso a todos)
  if(rol==='admin'){
    wrap.style.opacity='.5';wrap.style.pointerEvents='none';
    dwrap.style.opacity='.5';dwrap.style.pointerEvents='none';
    document.getElementById('usr-plantel').value='todos';
  } else {
    wrap.style.opacity='1';wrap.style.pointerEvents='auto';
    dwrap.style.opacity='1';dwrap.style.pointerEvents='auto';
  }
}
function saveUsuario(){
  document.getElementById('modal-usr').classList.remove('open');
  showToast('✅ Usuario guardado. Se envió correo de bienvenida.');
}

/* ══ MODAL PLANTEL ══ */
let modalDepts = [];
function openModalPlantel(){
  document.getElementById('modal-plantel-title').textContent='Nuevo plantel';
  document.getElementById('plantel-nombre').value='';
  document.getElementById('plantel-clave').value='';
  document.getElementById('plantel-dir').value='';
  document.getElementById('plantel-tel').value='';
  document.getElementById('plantel-email').value='';
  document.getElementById('plantel-notas').value='';
  modalDepts=[];
  renderModalDepts();
  switchModalTab('tab-info', document.querySelector('.modal-tab'));
  document.getElementById('modal-plantel').classList.add('open');
}
function openModalPlantelEdit(id){
  const p = plantelesData.find(x=>x.id===id);
  if(!p)return;
  document.getElementById('modal-plantel-title').textContent='Editar: '+p.nombre;
  document.getElementById('plantel-nombre').value=p.nombre;
  document.getElementById('plantel-dir').value=p.dir||'';
  modalDepts = p.depts.map(d=>d.nombre);
  renderModalDepts();
  switchModalTab('tab-info', document.querySelector('.modal-tab'));
  document.getElementById('modal-plantel').classList.add('open');
}
function addDeptToModal(){
  const input=document.getElementById('nuevo-dept-input');
  const val=input.value.trim();
  if(!val)return;
  modalDepts.push(val);
  input.value='';
  renderModalDepts();
}
function removeModalDept(i){
  modalDepts.splice(i,1);
  renderModalDepts();
}
function renderModalDepts(){
  const list=document.getElementById('depts-list');
  if(!modalDepts.length){
    list.innerHTML='<div style="text-align:center;font-size:.82rem;color:var(--gray-400);padding:1rem 0;">Sin departamentos agregados aún</div>';
    return;
  }
  list.innerHTML=modalDepts.map((d,i)=>`
    <div style="display:flex;align-items:center;justify-content:space-between;background:var(--gray-100);border-radius:9px;padding:.6rem 1rem;">
      <span style="font-size:.875rem;font-weight:500;color:var(--navy);">🏢 ${d}</span>
      <button onclick="removeModalDept(${i})" style="background:none;border:none;color:#c0392b;font-size:.85rem;cursor:pointer;padding:.1rem .3rem;border-radius:5px;" title="Eliminar">✕</button>
    </div>`).join('');
}
function savePlantel(){
  const nombre=document.getElementById('plantel-nombre').value.trim();
  if(!nombre){showToast('⚠️ Ingresa un nombre para el plantel');return;}
  document.getElementById('modal-plantel').classList.remove('open');
  showToast('✅ Plantel "'+nombre+'" guardado correctamente');
}
function switchModalTab(tabId, btn){
  document.querySelectorAll('.modal-tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.modal-tab').forEach(b=>b.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  btn.classList.add('active');
}

/* ══ DEPARTAMENTOS POR PLANTEL (select encadenado) ══ */
function updateDeptsByPlantel(plantelSelId, deptSelId){
  const plantel=document.getElementById(plantelSelId).value;
  const deptSel=document.getElementById(deptSelId);
  const depts=deptsByPlantel[plantel]||[];
  if(!depts.length){
    deptSel.innerHTML='<option value="">— Sin departamentos —</option>';
    return;
  }
  deptSel.innerHTML='<option value="">— Todos los departamentos —</option>'+
    depts.map(d=>`<option value="${d}">${d}</option>`).join('');
}

/* ══ TOAST ══ */
function showToast(msg){
  const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),3500);
}

/* ══ INIT ══ */
renderEmpleados();
renderPlanteles();
