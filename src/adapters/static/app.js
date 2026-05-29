/**
 * CheckBar - Frontend JavaScript
 * Conecta el dashboard de Stitch con el backend FastAPI.
 *
 * Endpoints consumidos:
 *  - GET  /productos  → Carga la tabla de inventario
 *  - POST /chat       → Envia mensajes al asistente Barman AI (RAG)
 */

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURACION
// ─────────────────────────────────────────────────────────────────────────────

const API_BASE = window.location.origin; // Mismo servidor que sirve el HTML
let allProducts = [];    // Cache de productos
let chatOpen = true;     // Estado del panel de chat

// ─────────────────────────────────────────────────────────────────────────────
// INICIALIZACION
// ─────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  loadInventory();
  setupSearchFilter();
  setupChatInput();
});

// ─────────────────────────────────────────────────────────────────────────────
// INVENTARIO: GET /productos
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Carga todos los productos desde el endpoint GET /productos
 * y actualiza la tabla y los KPIs.
 */
async function loadInventory() {
  showTableLoading();

  try {
    const response = await fetch(`${API_BASE}/productos`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const productos = await response.json();
    allProducts = productos;

    renderInventoryTable(productos);
    renderKPIs(productos);
    updateAlertBadge(productos);

  } catch (error) {
    showTableError(`No se pudo conectar a la API: ${error.message}`);
    console.error('[CheckBar] Error loading inventory:', error);
  }
}

/**
 * Renderiza la tabla de inventario con los datos de la API.
 * @param {Array} productos - Lista de productos del API
 */
function renderInventoryTable(productos) {
  const tbody = document.getElementById('inventory-body');
  const table = document.getElementById('inventory-table');
  const loading = document.getElementById('table-loading');
  const errorEl = document.getElementById('table-error');

  loading.classList.add('hidden');
  errorEl.classList.add('hidden');
  table.classList.remove('hidden');

  if (productos.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="py-xl text-center text-on-surface-variant font-body-lg text-body-lg">
          No hay productos en el inventario. Ejecuta el seeder primero.
        </td>
      </tr>`;
    return;
  }

  tbody.innerHTML = productos.map(p => createProductRow(p)).join('');
}

/**
 * Crea el HTML de una fila de la tabla para un producto.
 * @param {Object} p - Objeto producto de la API
 * @returns {string} HTML de la fila <tr>
 */
function createProductRow(p) {
  const stockPercent = p.stock_minimo > 0
    ? Math.min(100, Math.round((p.stock_actual / (p.stock_minimo * 4)) * 100))
    : 100;

  const isLow = p.tiene_stock_bajo;
  const stockClass = isLow ? 'stock-low' : 'stock-normal';
  const stockColor = isLow ? 'text-tertiary' : 'text-on-surface';
  const barColor = isLow
    ? 'bg-tertiary shadow-[0_0_8px_rgba(255,184,105,0.5)]'
    : 'bg-primary shadow-[0_0_8px_rgba(208,188,255,0.4)]';

  // Category icon selection
  const categoryIcons = {
    'Whisky': 'local_bar',
    'Vodka': 'wine_bar',
    'Ron': 'liquor',
    'Gin': 'local_drink',
    'Tequila': 'nightlife',
    'Mezcal': 'nightlife',
    'Cerveza': 'sports_bar',
    'default': 'inventory_2'
  };
  const icon = categoryIcons[p.categoria] || categoryIcons['default'];

  return `
    <tr class="hover:bg-white/[0.02] transition-colors group ${stockClass}" data-product-name="${escapeHtml(p.nombre.toLowerCase())}">
      <!-- Producto -->
      <td class="py-sm px-md">
        <div class="flex items-center gap-sm">
          <div class="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center border border-white/5 shrink-0">
            <span class="material-symbols-outlined text-on-surface-variant text-[20px]" style="font-variation-settings: 'FILL' 1;">${icon}</span>
          </div>
          <div>
            <p class="font-body-lg text-body-lg font-semibold text-on-surface">${escapeHtml(p.nombre)}</p>
            <p class="font-body-sm text-body-sm text-on-surface-variant text-[12px]">${escapeHtml(p.unidad_medida)} · ${escapeHtml(p.proveedor)}</p>
          </div>
        </div>
      </td>
      <!-- Categoria -->
      <td class="py-sm px-md">
        <span class="category-badge">${escapeHtml(p.categoria)}</span>
      </td>
      <!-- Stock con barra de progreso -->
      <td class="py-sm px-md">
        <div class="flex flex-col gap-xs w-48">
          <div class="flex justify-between font-body-sm text-body-sm">
            <span class="${stockColor} font-semibold">${p.stock_actual} uds.</span>
            <span class="text-on-surface-variant">Min: ${p.stock_minimo}</span>
          </div>
          <div class="w-full h-1.5 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full ${barColor} rounded-full stock-bar-fill" style="width: ${stockPercent}%"></div>
          </div>
        </div>
      </td>
      <!-- Precio -->
      <td class="py-sm px-md font-body-lg text-body-lg text-on-surface font-semibold">$${p.precio_unitario.toFixed(2)}</td>
      <!-- Margen -->
      <td class="py-sm px-md">
        <span class="font-body-sm text-body-sm ${p.margen_ganancia > 40 ? 'text-primary' : 'text-on-surface-variant'}">${p.margen_ganancia.toFixed(1)}%</span>
      </td>
      <!-- Estado -->
      <td class="py-sm px-md text-right">
        ${isLow
          ? `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-tertiary/10 border border-tertiary/30 font-label-caps text-label-caps text-tertiary">
               <span class="material-symbols-outlined text-[12px]">warning</span> STOCK BAJO
             </span>`
          : `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary/10 border border-primary/30 font-label-caps text-label-caps text-primary">
               <span class="material-symbols-outlined text-[12px]">check_circle</span> OK
             </span>`
        }
      </td>
    </tr>`;
}

// ─────────────────────────────────────────────────────────────────────────────
// KPIs
// ─────────────────────────────────────────────────────────────────────────────

function renderKPIs(productos) {
  const total = productos.length;
  const alertas = productos.filter(p => p.tiene_stock_bajo).length;
  const categorias = new Set(productos.map(p => p.categoria)).size;

  animateCounter('kpi-total', total);
  animateCounter('kpi-alertas', alertas);
  animateCounter('kpi-categorias', categorias);
}

function animateCounter(elementId, target) {
  const el = document.getElementById(elementId);
  if (!el) return;
  let start = 0;
  const duration = 600;
  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    el.textContent = Math.floor(progress * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target;
  };
  requestAnimationFrame(step);
}

function updateAlertBadge(productos) {
  const alertCount = productos.filter(p => p.tiene_stock_bajo).length;
  const badge = document.getElementById('alert-badge');
  if (alertCount > 0) {
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// BUSQUEDA / FILTRO
// ─────────────────────────────────────────────────────────────────────────────

function setupSearchFilter() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const rows = document.querySelectorAll('#inventory-body tr[data-product-name]');

    rows.forEach(row => {
      const name = row.dataset.productName || '';
      row.style.display = name.includes(query) ? '' : 'none';
    });
  });

  // Refresh button
  document.getElementById('btn-refresh')?.addEventListener('click', loadInventory);
}

// ─────────────────────────────────────────────────────────────────────────────
// UI STATES
// ─────────────────────────────────────────────────────────────────────────────

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
  const msgEl = document.getElementById('table-error-msg');
  if (msgEl) msgEl.textContent = message;
}

// ─────────────────────────────────────────────────────────────────────────────
// BARMAN AI CHAT: POST /chat
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

/**
 * Envia la pregunta al endpoint POST /chat y muestra la respuesta.
 */
async function sendChat() {
  const input = document.getElementById('chat-input');
  const pregunta = input?.value?.trim();
  if (!pregunta) return;

  input.value = '';
  hideSuggestionChips();

  // Mostrar mensaje del usuario
  appendMessage('user', pregunta);

  // Mostrar indicador de escritura
  const typingId = appendTypingIndicator();

  // Deshabilitar input mientras espera
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
      appendMessage('ai', `Error: ${err.detail || 'Respuesta inesperada del servidor.'}`);
    } else {
      const data = await response.json();
      appendMessage('ai', data.respuesta);
    }

  } catch (error) {
    removeTypingIndicator(typingId);
    appendMessage('ai', `No pude conectarme al servidor. Asegurate de que el backend este corriendo en ${API_BASE}`);
    console.error('[CheckBar] Chat error:', error);
  } finally {
    if (btn) btn.disabled = false;
    if (input) input.disabled = false;
    if (input) input.focus();
  }
}

/**
 * Envia un mensaje desde los chips de sugerencia.
 */
function sendSuggestion(text) {
  const input = document.getElementById('chat-input');
  if (input) input.value = text;
  sendChat();
}

/**
 * Agrega un mensaje al cuerpo del chat.
 */
function appendMessage(role, text) {
  const chatBody = document.getElementById('chat-body');
  if (!chatBody) return;

  const isAI = role === 'ai';
  const div = document.createElement('div');
  div.className = `chat-message flex gap-2 items-start ${isAI ? 'max-w-[92%]' : 'max-w-[85%] self-end flex-row-reverse'}`;

  if (isAI) {
    div.innerHTML = `
      <div class="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30 shrink-0 mt-1">
        <span class="material-symbols-outlined text-primary text-[14px]" style="font-variation-settings: 'FILL' 1;">smart_toy</span>
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

/**
 * Muestra el indicador de "escribiendo..." mientras espera respuesta.
 */
function appendTypingIndicator() {
  const chatBody = document.getElementById('chat-body');
  const id = `typing-${Date.now()}`;
  const div = document.createElement('div');
  div.id = id;
  div.className = 'flex gap-2 items-start max-w-[85%]';
  div.innerHTML = `
    <div class="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30 shrink-0 mt-1">
      <span class="material-symbols-outlined text-primary text-[14px]" style="font-variation-settings: 'FILL' 1;">smart_toy</span>
    </div>
    <div class="bg-surface-variant rounded-xl rounded-tl-none p-3 border border-white/5 shadow-sm flex items-center gap-1">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>`;
  chatBody?.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  document.getElementById(id)?.remove();
}

function hideSuggestionChips() {
  const chips = document.getElementById('suggestion-chips');
  if (chips) chips.style.display = 'none';
}

// ─────────────────────────────────────────────────────────────────────────────
// CHAT PANEL TOGGLE
// ─────────────────────────────────────────────────────────────────────────────

function toggleChat() {
  const panel = document.getElementById('ai-chat-panel');
  const icon = document.getElementById('chat-toggle-icon');
  chatOpen = !chatOpen;

  if (chatOpen) {
    panel.classList.remove('collapsed');
    if (icon) icon.textContent = 'keyboard_arrow_down';
  } else {
    panel.classList.add('collapsed');
    if (icon) icon.textContent = 'keyboard_arrow_up';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// UTILIDADES
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Escapa caracteres HTML para prevenir XSS.
 */
function escapeHtml(text) {
  if (typeof text !== 'string') return String(text || '');
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}
