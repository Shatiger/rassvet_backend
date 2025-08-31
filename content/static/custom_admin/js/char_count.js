document.addEventListener("DOMContentLoaded", function () {
  const fields = document.querySelectorAll("input[data-charcount], textarea[data-charcount]");

  fields.forEach((field) => {
    if (field.dataset.charcountRendered === "1") return;

    const wrap =
      field.closest(".form-row, .form-group, .field-box, .flex-container, .form-row .fieldBox") ||
      field.parentNode;

    const counter = document.createElement("div");
    counter.className = "char-count-hint";

    const min = parseInt(field.getAttribute("data-min") || "0", 10);
    const max = parseInt(field.getAttribute("data-max") || "0", 10);

    function render() {
      const len = field.value.length;
      const parts = [];
      if (min) parts.push(`минимум ${min}`);
      if (max) parts.push(`максимум ${max}`);
      counter.textContent =
        parts.length ? `Введено символов: ${len} (рекомендация: ${parts.join(", ")})`
                     : `Введено символов: ${len}`;

      const invalid = (max && len > max) || (min && len < min);
      counter.classList.toggle("is-invalid", invalid);
    }

    const help = wrap.querySelector(".help");
    if (help) {
      help.appendChild(counter);
    } else {
      field.insertAdjacentElement("afterend", counter);
    }

    field.addEventListener("input", render);
    render();

    field.dataset.charcountRendered = "1";
  });
});
