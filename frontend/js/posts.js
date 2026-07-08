function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

const urlParams = new URLSearchParams(window.location.search);

const state = {
  page: 1,
  limit: 10,
  q: "",
  userId: urlParams.get("userId") || "",
};

let usersById = {};

function excerpt(body, len = 100) {
  const clean = body.replace(/\s+/g, " ").trim();
  return clean.length > len ? `${clean.slice(0, len)}...` : clean;
}

function postCard(p) {
  const author = usersById[p.userId];
  return `
    <div class="card">
      <a class="title" href="post.html?id=${p.id}">${escapeHtml(p.title)}</a>
      <div class="meta">par ${escapeHtml(author?.name ?? `utilisateur #${p.userId}`)}</div>
      <div class="excerpt">${escapeHtml(excerpt(p.body))}</div>
    </div>
  `;
}

function renderPagination(meta) {
  const visible = meta.totalPages > 1;
  document.getElementById("pagination").hidden = !visible;
  if (!visible) return;
  document.getElementById("prevPage").disabled = meta.page <= 1;
  document.getElementById("nextPage").disabled = meta.page >= meta.totalPages;
  document.getElementById("pageInfo").textContent = `Page ${meta.page} / ${meta.totalPages}`;
}

async function loadAuthorFilter() {
  const select = document.getElementById("authorFilter");
  try {
    const users = await api.users();
    usersById = Object.fromEntries(users.map((u) => [u.id, u]));
    select.innerHTML += users.map((u) =>
      `<option value="${u.id}" ${String(u.id) === String(state.userId) ? "selected" : ""}>${u.name}</option>`
    ).join("");
  } catch (err) {
    console.error("Could not load authors for filter", err);
  }
}

async function loadPosts() {
  const content = document.getElementById("content");
  content.className = "state-msg";
  content.textContent = "Chargement...";

  try {
    const data = await api.posts(state);

    if (!data.items.length) {
      content.textContent = "Aucun article ne correspond à ces critères.";
      renderPagination(data);
      return;
    }

    content.className = "";
    content.innerHTML = data.items.map(postCard).join("");
    renderPagination(data);
  } catch (err) {
    content.className = "error-msg";
    content.textContent = `Erreur de chargement : ${err.message}`;
    document.getElementById("pagination").hidden = true;
  }
}

document.getElementById("search").addEventListener("input", (e) => {
  state.q = e.target.value;
  state.page = 1;
  clearTimeout(window._searchDebounce);
  window._searchDebounce = setTimeout(loadPosts, 300);
});

document.getElementById("authorFilter").addEventListener("change", (e) => {
  state.userId = e.target.value;
  state.page = 1;
  loadPosts();
});

document.getElementById("prevPage").addEventListener("click", () => { state.page -= 1; loadPosts(); });
document.getElementById("nextPage").addEventListener("click", () => { state.page += 1; loadPosts(); });

(async function init() {
  await loadAuthorFilter();
  await loadPosts();
})();
