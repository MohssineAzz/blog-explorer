function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function renderPost() {
  const content = document.getElementById("content");
  const id = new URLSearchParams(window.location.search).get("id");

  if (!id) {
    content.className = "error-msg";
    content.textContent = "Aucun identifiant d'article fourni.";
    return;
  }

  try {
    const post = await api.post(id);

    const commentsHtml = post.comments.length
      ? post.comments
          .map(
            (c) => `
        <div class="comment">
          <span class="name">${escapeHtml(c.name)}</span>
          <span class="email">${escapeHtml(c.email)}</span>
          <div>${escapeHtml(c.body)}</div>
        </div>
      `
          )
          .join("")
      : '<p class="meta">Pas encore de commentaire.</p>';

    content.className = "";
    content.innerHTML = `
      <h1>${escapeHtml(post.title)}</h1>
      <div class="meta">
        par <a href="index.html">${escapeHtml(post.author.name)}</a>
        (${escapeHtml(post.author.email)})
      </div>
      <div class="post-body">${escapeHtml(post.body)}</div>
      <h2>Commentaires (${post.comments.length})</h2>
      ${commentsHtml}
    `;
  } catch (err) {
    content.className = "error-msg";
    content.textContent = `Erreur de chargement : ${err.message}`;
  }
}

renderPost();
