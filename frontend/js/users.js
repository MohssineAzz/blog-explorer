function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function renderUsers() {
  const content = document.getElementById("content");
  try {
    const users = await api.users();
    if (!users.length) {
      content.className = "state-msg";
      content.textContent = "Aucun auteur trouvé.";
      return;
    }

    content.className = "";
    content.innerHTML = users
      .map(
        (u) => `
      <div class="card">
        <div class="title">${escapeHtml(u.name)}</div>
        <div class="meta">@${escapeHtml(u.username)} &middot; ${escapeHtml(u.email)}</div>
        <div class="meta">${escapeHtml(u.company?.name || "")} &middot; ${escapeHtml(u.address?.city || "")}</div>
        <div class="excerpt"><a href="posts.html?userId=${u.id}">Voir les articles de ${escapeHtml(u.name)} &rarr;</a></div>
      </div>
    `
      )
      .join("");
  } catch (err) {
    content.className = "error-msg";
    content.textContent = `Erreur de chargement : ${err.message}`;
  }
}

renderUsers();
