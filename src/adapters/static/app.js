/**
 * CheckBar - Frontend JavaScript
 * Conecta el dashboard de Stitch con el backend FastAPI.
 */

const API_BASE = window.location.origin;
let allProducts = [];
let chatOpen = true;

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  loadInventory();
  setupSearchFilter();
  setupChatInput();
  setupVentaForm();
  setupProductoForm();
});

// ─────────────────────────────────────────────────────────────────────────────
// NAVEGACION SPA
// ─────────────────────────────────────────────────────────────────────────────
function setupNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  const views = document.querySelectorAll('.spa-view');

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Update classes for links
      navLinks.forEach(l => {
        l.classList.remove('border-r-2', 'border-primary', 'bg-primary/5', 'text-primary', 'font-bold');
        l.classList.add('text-on-surface-variant', 'hover:bg-primary/10', 'hover:text-primary');
      });
      e.currentTarget.classList.add('border-r-2', 'border-primary', 'bg-primary/5', 'text-primary', 'font-bold');
      e.currentTarget.classList.remove('text-on-surface-variant', 'hover:bg-primary/10', 'hover:text-primary');

      // Switch view
      const targetId = e.currentTarget.getAttribute('data-target');
      views.forEach(view => {
        if (view.id === targetId) {
          view.classList.add('active');
        } else {
          view.classList.remove('active');
        }
      });
    });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// INVENTARIO: GET /productos
// ─────────────────────────────────────────────────────────────────────────────

async function loadInventory() {
  showTableLoading();
  try {
    const response = await fetch(`${API_BASE}/productos`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const productos = await response.json();
    allProducts = productos;

    renderInventoryTable(productos);
    renderKPIs(productos);
    updateAlertBadge(productos);
    populateVentaDropdown(productos); // Update dropdown in Nueva Venta
  } catch (error) {
    showTableError(`No se pudo conectar a la API: ${error.message}`);
  }
}

function renderInventoryTable(productos) {
  const tbody = document.getElementById('inventory-body');
  const table = document.getElementById('inventory-table');
  const loading = document.getElementById('table-loading');
  const errorEl = document.getElementById('table-error');

  loading.classList.add('hidden');
  errorEl.classList.add('hidden');
  table.classList.remove('hidden');

  if (productos.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="py-xl text-center">No hay productos.</td></tr>`;
    return;
  }
  tbody.innerHTML = productos.map(p => createProductRow(p)).join('');
}

function createProductRow(p) {
  const stockPercent = p.stock_minimo > 0 ? Math.min(100, Math.round((p.stock_actual / (p.stock_minimo * 4)) * 100)) : 100;
  const isLow = p.tiene_stock_bajo;
  const stockClass = isLow ? 'stock-low' : 'stock-normal';
  const stockColor = isLow ? 'text-tertiary' : 'text-on-surface';
  const barColor = isLow ? 'bg-tertiary shadow-[0_0_8px_rgba(255,184,105,0.5)]' : 'bg-primary shadow-[0_0_8px_rgba(208,188,255,0.4)]';

  const categoryIcons = {'Whisky': 'local_bar', 'Vodka': 'wine_bar', 'Ron': 'liquor', 'Gin': 'local_drink', 'Tequila': 'nightlife', 'Cerveza': 'sports_bar', 'default': 'inventory_2'};
  const icon = categoryIcons[p.categoria] || categoryIcons['default'];

  return `
    <tr class="hover:bg-white/[0.02] transition-colors group ${stockClass}" data-product-name="${escapeHtml(p.nombre.toLowerCase())}">
      <td class="py-sm px-md">
        <div class="flex items-center gap-sm">
          <div class="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center border border-white/5 shrink-0">
            <span class="material-symbols-outlined text-on-surface-variant text-[20px]">${icon}</span>
          </div>
          <div>
            <p class="font-body-lg font-semibold text-on-surface">${escapeHtml(p.nombre)}</p>
            <p class="font-body-sm text-on-surface-variant text-[12px]">${escapeHtml(p.unidad_medida)} · ${escapeHtml(p.proveedor)}</p>
          </div>
        </div>
      </td>
      <td class="py-sm px-md"><span class="category-badge">${escapeHtml(p.categoria)}</span></td>
      <td class="py-sm px-md">
        <div class="flex flex-col gap-xs w-48">
          <div class="flex justify-between text-sm">
            <span class="${stockColor} font-semibold">${p.stock_actual} uds.</span>
            <span class="text-on-surface-variant">Min: ${p.stock_minimo}</span>
          </div>
          <div class="w-full h-1.5 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full ${barColor} rounded-full" style="width: ${stockPercent}%"></div>
          </div>
        </div>
      </td>
      <td class="py-sm px-md font-body-lg text-on-surface font-semibold">$${p.precio_unitario.toFixed(2)}</td>
      <td class="py-sm px-md"><span class="text-sm ${p.margen_ganancia > 40 ? 'text-primary' : 'text-on-surface-variant'}">${p.margen_ganancia.toFixed(1)}%</span></td>
      <td class="py-sm px-md text-right">
        ${isLow ? `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-tertiary/10 border border-tertiary/30 text-xs text-tertiary">STOCK BAJO</span>` : `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary/10 border border-primary/30 text-xs text-primary">OK</span>`}
      </td>
    </tr>`;
}

function renderKPIs(productos) {
  document.getElementById('kpi-total').textContent = productos.length;
  document.getElementById('kpi-alertas').textContent = productos.filter(p => p.tiene_stock_bajo).length;
  document.getElementById('kpi-categorias').textContent = new Set(productos.map(p => p.categoria)).size;
}
function updateAlertBadge(productos) {
  const alertCount = productos.filter(p => p.tiene_stock_bajo).length;
  const badge = document.getElementById('alert-badge');
  badge.classList.toggle('hidden', alertCount === 0);
}

// ─────────────────────────────────────────────────────────────────────────────
// FORMS: NUEVA VENTA & AÑADIR PRODUCTO
// ─────────────────────────────────────────────────────────────────────────────

function populateVentaDropdown(productos) {
  const select = document.getElementById('venta-producto');
  if(!select) return;
  select.innerHTML = '<option value="">Selecciona un producto...</option>' + 
    productos.map(p => `<option value="${p.id}" data-precio="${p.precio_unitario}">${escapeHtml(p.nombre)} - $${p.precio_unitario} (Stock: ${p.stock_actual})</option>`).join('');
}

function setupVentaForm() {
  const form = document.getElementById('form-venta');
  const errEl = document.getElementById('venta-error');
  const sucEl = document.getElementById('venta-success');

  if(!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errEl.classList.add('hidden');
    sucEl.classList.add('hidden');

    const select = document.getElementById('venta-producto');
    const cantidad = parseInt(document.getElementById('venta-cantidad').value);
    const metodo = document.getElementById('venta-metodo').value;
    const productoId = parseInt(select.value);

    if(!productoId) return;
    const option = select.options[select.selectedIndex];
    const precio = parseFloat(option.dataset.precio);

    try {
      const response = await fetch(`${API_BASE}/ventas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lineas: [{ producto_id: productoId, cantidad, precio_unitario: precio }],
          metodo_pago: metodo
        })
      });

      if(!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar venta');
      }

      const result = await response.json();
      sucEl.textContent = `Venta ${result.numero_factura} registrada exitosamente. Total: $${result.total}`;
      sucEl.classList.remove('hidden');
      form.reset();
      loadInventory(); // Reload to update stock
      
      // Generar PDF (Factura ficticia)
      if (window.jspdf) {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        doc.setFontSize(22);
        doc.text("CheckBar - Ticket de Venta", 20, 20);
        
        doc.setFontSize(12);
        doc.text(`Factura N°: ${result.numero_factura}`, 20, 35);
        doc.text(`Fecha: ${new Date().toLocaleString()}`, 20, 42);
        doc.text(`Método de Pago: ${result.metodo_pago}`, 20, 49);
        
        doc.text("---------------------------------------------------------", 20, 60);
        doc.text("Producto", 20, 65);
        doc.text("Cant.", 120, 65);
        doc.text("Precio", 150, 65);
        doc.text("Subtotal", 180, 65);
        doc.text("---------------------------------------------------------", 20, 70);
        
        let yPos = 80;
        result.lineas.forEach(linea => {
            const prodName = option.text.split(' - ')[0]; // Basic product name fallback
            doc.text(prodName.substring(0, 35), 20, yPos);
            doc.text(`${linea.cantidad}`, 125, yPos);
            doc.text(`$${linea.precio_unitario.toFixed(2)}`, 150, yPos);
            doc.text(`$${(linea.cantidad * linea.precio_unitario).toFixed(2)}`, 180, yPos);
            yPos += 10;
        });
        
        doc.text("---------------------------------------------------------", 20, yPos + 5);
        doc.setFontSize(14);
        doc.setFont(undefined, 'bold');
        doc.text(`TOTAL: $${result.total.toFixed(2)}`, 150, yPos + 15);
        
        doc.save(`Factura_${result.numero_factura}.pdf`);
      }

    } catch(err) {
      errEl.textContent = err.message;
      errEl.classList.remove('hidden');
    }
  });
}

function setupProductoForm() {
  const modal = document.getElementById('modal-add-product');
  const btnOpen = document.getElementById('btn-add-product');
  const btnCancel = document.getElementById('btn-cancel-product');
  const form = document.getElementById('form-producto');
  const errEl = document.getElementById('prod-error');

  if(!modal) return;
  btnOpen.addEventListener('click', () => modal.classList.remove('hidden'));
  btnCancel.addEventListener('click', () => modal.classList.add('hidden'));

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errEl.classList.add('hidden');

    const data = {
      nombre: document.getElementById('prod-nombre').value,
      categoria: document.getElementById('prod-categoria').value,
      precio_unitario: parseFloat(document.getElementById('prod-precio-u').value),
      precio_costo: parseFloat(document.getElementById('prod-precio-c').value),
      stock_actual: parseInt(document.getElementById('prod-stock-a').value),
      stock_minimo: parseInt(document.getElementById('prod-stock-m').value),
      unidad_medida: document.getElementById('prod-unidad').value,
      proveedor: document.getElementById('prod-proveedor').value,
    };

    try {
      const response = await fetch(`${API_BASE}/productos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if(!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Error al añadir producto');
      }
      
      form.reset();
      modal.classList.add('hidden');
      loadInventory();
    } catch(err) {
      errEl.textContent = err.message;
      errEl.classList.remove('hidden');
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// BUSQUEDA Y UI
// ─────────────────────────────────────────────────────────────────────────────

function setupSearchFilter() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return;
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const rows = document.querySelectorAll('#inventory-body tr[data-product-name]');
    rows.forEach(row => {
      row.style.display = row.dataset.productName.includes(query) ? '' : 'none';
    });
  });
  document.getElementById('btn-refresh')?.addEventListener('click', loadInventory);
}

function showTableLoading() {
  document.getElementById('table-loading').classList.remove('hidden');
  document.getElementById('inventory-table').classList.add('hidden');
  document.getElementById('table-error').classList.add('hidden');
}

function showTableError(message) {
  document.getElementById('table-loading').classList.add('hidden');
  document.getElementById('inventory-table').classList.add('hidden');
  const errorEl = document.getElementById('table-error');
  errorEl.classList.remove('hidden');
  errorEl.classList.add('flex');
  document.getElementById('table-error-msg').textContent = message;
}

// ─────────────────────────────────────────────────────────────────────────────
// BARMAN AI CHAT
// ─────────────────────────────────────────────────────────────────────────────

function setupChatInput() {
  const input = document.getElementById('chat-input');
  if (!input) return;
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  });
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const pregunta = input?.value?.trim();
  if (!pregunta) return;
  input.value = '';
  document.getElementById('suggestion-chips').style.display = 'none';

  appendMessage('user', pregunta);
  const typingId = appendTypingIndicator();
  const btn = document.getElementById('btn-send-chat');
  if (btn) btn.disabled = true;
  if (input) input.disabled = true;

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pregunta }),
    });
    removeTypingIndicator(typingId);
    if (!response.ok) {
      const err = await response.json();
      appendMessage('ai', `Error: ${err.detail || 'Respuesta inesperada'}`);
    } else {
      const data = await response.json();
      appendMessage('ai', data.respuesta);
    }
  } catch (error) {
    removeTypingIndicator(typingId);
    appendMessage('ai', `Error de conexión: ${error.message}`);
  } finally {
    if (btn) btn.disabled = false;
    if (input) { input.disabled = false; input.focus(); }
  }
}

function sendSuggestion(text) {
  document.getElementById('chat-input').value = text;
  sendChat();
}

function appendMessage(role, text) {
  const chatBody = document.getElementById('chat-body');
  const isAI = role === 'ai';
  const div = document.createElement('div');
  div.className = `chat-message flex gap-2 items-start ${isAI ? 'max-w-[92%]' : 'max-w-[85%] self-end flex-row-reverse'}`;
  
  if (isAI) {
    div.innerHTML = `
      <div class="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30 shrink-0 mt-1">
        <span class="material-symbols-outlined text-primary text-[14px]">smart_toy</span>
      </div>
      <div class="bg-surface-variant rounded-xl rounded-tl-none p-3 border border-white/5 shadow-sm">
        <p class="font-body-sm text-body-sm text-on-surface whitespace-pre-wrap">${escapeHtml(text)}</p>
      </div>`;
  } else {
    div.innerHTML = `
      <div class="bg-primary/20 rounded-xl rounded-tr-none p-3 border border-primary/20 shadow-sm">
        <p class="font-body-sm text-body-sm text-primary whitespace-pre-wrap">${escapeHtml(text)}</p>
      </div>`;
  }
  chatBody.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
}

function appendTypingIndicator() {
  const chatBody = document.getElementById('chat-body');
  const id = `typing-${Date.now()}`;
  const div = document.createElement('div');
  div.id = id;
  div.className = 'flex gap-2 items-start max-w-[85%]';
  div.innerHTML = `
    <div class="w-6 h-6 rounded-full bg-primary/20 flex flex-col justify-center border border-primary/30 shrink-0 mt-1 text-center font-bold text-primary">...</div>
  `;
  chatBody.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  document.getElementById(id)?.remove();
}

function toggleChat() {
  const panel = document.getElementById('ai-chat-panel');
  chatOpen = !chatOpen;
  panel.style.transform = chatOpen ? 'translateY(0)' : 'translateY(calc(100% - 60px))';
}

function escapeHtml(text) {
  if (typeof text !== 'string') return String(text || '');
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}
