/**
 * CheckBar - Frontend JavaScript
 * Conecta el dashboard de Stitch con el backend FastAPI.
 */

const API_BASE = window.location.origin;
let allProducts = [];
let ventasCache = [];  // Cache para redibujar top productos tras cargar inventario
let salesChartInstance = null;
let chatOpen = true;

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  loadInventory();
  setupSearchFilter();
  setupChatInput();
  setupVentaForm();
  setupProductoForm();
  loadSalesChart();
  loadAIStatus();
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
    populateVentaDropdown(productos);

    // Si ya hay ventas en cache, redibujar top productos con nombres correctos
    if (ventasCache.length > 0) {
      loadTopProductsChart(ventasCache);
    }
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

function updateKPIsFromVentas(ventas) {
  // Obtener fecha local en formato YYYY-MM-DD (sin problemas de zona horaria UTC)
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hoy = `${year}-${month}-${day}`;
  
  const ventasHoy = ventas.filter(v => v.fecha_venta && v.fecha_venta.startsWith(hoy));
  document.getElementById('kpi-ventas-hoy').textContent = ventasHoy.length;

  const hace7Dias = new Date();
  hace7Dias.setDate(hace7Dias.getDate() - 7);
  const ventas7d = ventas.filter(v => v.fecha_venta && new Date(v.fecha_venta) >= hace7Dias);
  const ingresos7d = ventas7d.reduce((sum, v) => sum + v.total, 0);
  document.getElementById('kpi-ingresos').textContent = '$' + ingresos7d.toFixed(0);
}
function updateAlertBadge(productos) {
  const alertCount = productos.filter(p => p.tiene_stock_bajo).length;
  const badge = document.getElementById('alert-badge');
  badge.classList.toggle('hidden', alertCount === 0);
  if (alertCount > 0) {
    badge.textContent = alertCount > 9 ? '9+' : alertCount;
    badge.className = badge.className.replace('w-2 h-2', '');
    badge.style.cssText = 'min-width:16px;height:16px;font-size:10px;display:flex;align-items:center;justify-content:center;padding:0 3px;';
  }
  setupAlertsButton(productos);
}

function setupAlertsButton(productos) {
  const btn = document.getElementById('btn-alerts');
  if (!btn) return;
  // Remove previous listener
  btn.replaceWith(btn.cloneNode(true));
  const freshBtn = document.getElementById('btn-alerts');
  freshBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    showAlertsPanel(productos);
  });
}

function showAlertsPanel(productos) {
  // Remove existing panel
  document.getElementById('alerts-panel')?.remove();

  const bajos = productos.filter(p => p.tiene_stock_bajo);
  const panel = document.createElement('div');
  panel.id = 'alerts-panel';
  panel.className = 'fixed top-16 right-8 w-80 z-50 glass-panel rounded-xl shadow-2xl border border-white/10 overflow-hidden';
  panel.style.animation = 'fadeInDown 0.2s ease';

  panel.innerHTML = `
    <div class="px-4 py-3 border-b border-white/10 flex justify-between items-center bg-surface-container-low/80">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-tertiary text-[18px]">warning</span>
        <span class="font-semibold text-on-surface text-sm">Alertas de Stock</span>
      </div>
      <button onclick="document.getElementById('alerts-panel').remove()" class="text-on-surface-variant hover:text-white">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    </div>
    <div class="max-h-72 overflow-y-auto divide-y divide-white/5">
      ${bajos.length === 0
        ? `<div class="p-4 text-center text-on-surface-variant text-sm">✅ Todo el stock está en orden</div>`
        : bajos.map(p => `
          <div class="px-4 py-3 flex justify-between items-center hover:bg-white/5 transition-colors">
            <div>
              <p class="text-sm font-medium text-on-surface">${escapeHtml(p.nombre)}</p>
              <p class="text-xs text-on-surface-variant">${p.categoria}</p>
            </div>
            <div class="text-right shrink-0 ml-2">
              <p class="text-tertiary font-bold text-sm">${p.stock_actual} uds.</p>
              <p class="text-xs text-on-surface-variant">Mín: ${p.stock_minimo}</p>
            </div>
          </div>`).join('')}
    </div>
    ${bajos.length > 0 ? `
    <div class="px-4 py-2 bg-tertiary/10 border-t border-white/5">
      <p class="text-xs text-tertiary text-center">${bajos.length} producto${bajos.length > 1 ? 's' : ''} requiere${bajos.length > 1 ? 'n' : ''} reposición</p>
    </div>` : ''}
  `;

  document.body.appendChild(panel);

  // Close on outside click
  setTimeout(() => {
    document.addEventListener('click', function closePanel(ev) {
      if (!panel.contains(ev.target)) {
        panel.remove();
        document.removeEventListener('click', closePanel);
      }
    });
  }, 50);
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
      loadSalesChart(); // Reload sales chart
      
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

  // Wire up reset button if present
  const btnReset = document.getElementById('btn-reset-chat');
  if (btnReset) {
    btnReset.addEventListener('click', resetChat);
  }
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

async function resetChat() {
  try {
    await fetch(`${API_BASE}/chat/reset`, { method: 'POST' });
  } catch(e) { /* ignore */ }
  const chatBody = document.getElementById('chat-body');
  if (chatBody) chatBody.innerHTML = '';
  const chips = document.getElementById('suggestion-chips');
  if (chips) chips.style.display = '';
  appendMessage('ai', 'Historial limpiado. ¿En qué puedo ayudarte?');
}

function escapeHtml(text) {
  if (typeof text !== 'string') return String(text || '');
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

async function loadAIStatus() {
  try {
    const r = await fetch(`${API_BASE}/chat/status`);
    if (!r.ok) return;
    const data = await r.json();
    const statusEl = document.getElementById('ai-status');
    const dotEl = document.getElementById('ai-live-dot');
    if (statusEl) {
      if (data.gemini_configurado) {
        statusEl.textContent = '✨ Gemini 2.0 Flash';
        statusEl.style.color = '#D0BCFF';
        if (dotEl) dotEl.style.background = '#D0BCFF';
      } else {
        statusEl.textContent = `Local · ${data.modelo_local}`;
        statusEl.style.color = '';
      }
    }
  } catch(e) {
    const statusEl = document.getElementById('ai-status');
    if (statusEl) statusEl.textContent = 'IA Local';
  }
}

let topProductsChartInstance = null;

async function loadSalesChart() {
  try {
    const response = await fetch(`${API_BASE}/ventas`);
    if(!response.ok) return;
    const ventas = await response.json();

    // Update ventas KPIs
    updateKPIsFromVentas(ventas);

    // ── LINE CHART: Sales by date ──
    const salesByDate = {};
    ventas.forEach(v => {
      if (!v.fecha_venta) return;
      const dateStr = v.fecha_venta.split('T')[0];
      salesByDate[dateStr] = (salesByDate[dateStr] || 0) + v.total;
    });
    const dates = Object.keys(salesByDate).sort().slice(-30);
    const totals = dates.map(d => salesByDate[d]);

    const ctx = document.getElementById('salesChart').getContext('2d');
    if (salesChartInstance) salesChartInstance.destroy();

    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(208, 188, 255, 0.45)');
    gradient.addColorStop(1, 'rgba(208, 188, 255, 0.0)');

    salesChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates.length ? dates : ['Sin ventas'],
        datasets: [{
          label: 'Ingresos ($)',
          data: totals.length ? totals : [0],
          borderColor: '#D0BCFF',
          backgroundColor: gradient,
          borderWidth: 2.5,
          pointBackgroundColor: '#F2B8B5',
          pointBorderColor: '#fff',
          pointRadius: 3,
          pointHoverRadius: 6,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(28,27,31,0.92)', titleColor: '#fff',
            bodyColor: '#D0BCFF', padding: 10, cornerRadius: 8, displayColors: false,
            callbacks: { label: (ctx) => '$' + ctx.parsed.y.toFixed(2) }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false },
            ticks: { color: '#CAC4D0', callback: v => '$' + v }
          },
          x: {
            grid: { display: false, drawBorder: false },
            ticks: { color: '#CAC4D0', maxTicksLimit: 8 }
          }
        }
      }
    });

    // ── BAR CHART: Top 7 products by revenue ──
    ventasCache = ventas;  // Guardar para cuando lleguen los productos
    loadTopProductsChart(ventas);

  } catch(err) {
    console.error('Error loading sales chart', err);
  }
}

function loadTopProductsChart(ventas) {
  try {
    // Aggregate revenue per product_id from lineas
    const revenueByProduct = {};
    ventas.forEach(v => {
      (v.lineas || []).forEach(l => {
        revenueByProduct[l.producto_id] = (revenueByProduct[l.producto_id] || 0) + l.subtotal;
      });
    });

    // Sort and pick top 7
    const sorted = Object.entries(revenueByProduct)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 7);

    // Match product ids to names — use full name, take first 3 words max
    const labels = sorted.map(([id]) => {
      const p = allProducts.find(pr => pr.id === parseInt(id));
      if (p) {
        const words = p.nombre.split(' ');
        return words.length > 3 ? words.slice(0, 3).join(' ') : p.nombre;
      }
      return 'Prod. ' + id;
    });
    const data = sorted.map(([, rev]) => parseFloat(rev.toFixed(2)));

    const ctx2 = document.getElementById('topProductsChart').getContext('2d');
    if (topProductsChartInstance) topProductsChartInstance.destroy();

    const colors = [
      'rgba(208,188,255,0.8)', 'rgba(242,184,181,0.8)', 'rgba(100,180,255,0.8)',
      'rgba(255,200,100,0.8)', 'rgba(130,220,170,0.8)', 'rgba(255,150,200,0.8)', 'rgba(160,200,255,0.8)'
    ];

    topProductsChartInstance = new Chart(ctx2, {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['Sin datos'],
        datasets: [{
          label: 'Ingresos ($)',
          data: data.length ? data : [0],
          backgroundColor: colors.slice(0, data.length),
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(28,27,31,0.92)', titleColor: '#fff',
            bodyColor: '#D0BCFF', padding: 8, cornerRadius: 6, displayColors: false,
            callbacks: { label: (ctx) => '$' + ctx.parsed.x.toFixed(2) }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false },
            ticks: { color: '#CAC4D0', callback: v => '$' + v }
          },
          y: {
            grid: { display: false, drawBorder: false },
            ticks: { color: '#CAC4D0', font: { size: 11 } }
          }
        }
      }
    });
  } catch(err) {
    console.error('Error loading top products chart', err);
  }
}
