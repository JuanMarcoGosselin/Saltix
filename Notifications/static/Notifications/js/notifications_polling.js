(function () {
  const POLL_INTERVAL_MS = 15000;

  function truncate(text, maxLength) {
    if (!text) return "";
    return text.length > maxLength ? `${text.slice(0, maxLength - 1)}...` : text;
  }

  function renderCount(menu, count) {
    const bell = menu.querySelector(".notification-bell");
    if (!bell) return;

    let badge = bell.querySelector(".notification-count");
    if (!count) {
      if (badge) badge.remove();
      return;
    }

    if (!badge) {
      badge = document.createElement("span");
      badge.className = "notification-count";
      bell.appendChild(badge);
    }
    badge.textContent = count > 99 ? "99+" : String(count);
  }

  function renderItems(menu, notifications) {
    const items = menu.querySelector(".notification-dropdown-items");
    const listUrl = menu.dataset.notificationsListUrl || "/notificaciones/";
    if (!items) return;

    items.replaceChildren();

    if (!notifications.length) {
      const empty = document.createElement("div");
      empty.className = "notification-dropdown-empty";
      empty.textContent = "No tienes notificaciones.";
      items.appendChild(empty);
      return;
    }

    notifications.forEach((notification) => {
      const link = document.createElement("a");
      link.className = "notification-dropdown-item";
      link.href = notification.url || listUrl;
      link.dataset.notificationLink = "1";
      link.dataset.markReadUrl = notification.mark_read_url || "";

      const title = document.createElement("strong");
      title.textContent = notification.title || "Notificacion";

      const message = document.createElement("span");
      message.textContent = truncate(notification.message || "", 90);

      link.append(title, message);
      items.appendChild(link);
    });
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  async function markReadBeforeNavigate(event) {
    const link = event.target.closest("[data-notification-link]");
    if (!link || event.defaultPrevented) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;

    const markReadUrl = link.dataset.markReadUrl;
    const destination = link.href;
    if (!markReadUrl || !destination) return;

    event.preventDefault();
    try {
      const body = new URLSearchParams();
      body.set("next", destination);
      await fetch(markReadUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": getCsrfToken(),
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        credentials: "same-origin",
        body: body.toString(),
      });
    } catch (error) {
      // El enlace debe seguir funcionando aunque no se logre marcar en ese intento.
    } finally {
      window.location.href = destination;
    }
  }

  async function refreshMenu(menu) {
    const url = menu.dataset.notificationsUrl;
    if (!url || menu.dataset.loading === "1") return;

    menu.dataset.loading = "1";
    try {
      const response = await fetch(url, {
        headers: { "Accept": "application/json" },
        credentials: "same-origin",
      });
      if (!response.ok) return;

      const data = await response.json();
      if (!data.ok) return;

      renderCount(menu, Number(data.unread_count || 0));
      renderItems(menu, data.notifications || []);
    } catch (error) {
      return;
    } finally {
      menu.dataset.loading = "0";
    }
  }

  function startPolling() {
    const menus = Array.from(document.querySelectorAll(".notification-menu"));
    if (!menus.length) return;

    menus.forEach((menu) => refreshMenu(menu));
    window.setInterval(() => {
      menus.forEach((menu) => refreshMenu(menu));
    }, POLL_INTERVAL_MS);

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") {
        menus.forEach((menu) => refreshMenu(menu));
      }
    });
    document.addEventListener("click", markReadBeforeNavigate);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startPolling);
  } else {
    startPolling();
  }
})();
