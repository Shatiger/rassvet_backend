document.addEventListener("DOMContentLoaded", function () {
  const fields = document.querySelectorAll("input[data-charcount], textarea[data-charcount]");

  fields.forEach((field) => {
    if (field.dataset.charcountRendered === "1") return;

    const counter = document.createElement("div");
    counter.className = "char-count-hint";

    const min = parseInt(field.getAttribute("data-min") || "0", 10);
    const max = parseInt(field.getAttribute("data-max") || "0", 10);

    function render() {
      const len = field.value.length;
      const parts = [];
      if (min) parts.push(`минимум ${min}`);
      if (max) parts.push(`максимум ${max}`);
      counter.textContent = parts.length
        ? `Введено символов: ${len} (рекомендация: ${parts.join(", ")})`
        : `Введено символов: ${len}`;

      const invalid = (max && len > max) || (min && len < min);
      counter.classList.toggle("is-invalid", invalid);
    }

    const wrap =
      field.closest(".form-row, .form-group, .field-box, .inline-related, .form-row .fieldBox") ||
      field.parentNode;
    const flexAncestor = field.closest(".flex-container, .field-flex, .related-widget-wrapper");
    const formRow = field.closest(".form-row, .inline-related, .field-box");

    const help = wrap && wrap.querySelector ? wrap.querySelector(".help") : null;

    if (help) {
      help.appendChild(counter);
    } else if (formRow) {
      formRow.appendChild(counter);
    } else if (flexAncestor && flexAncestor.parentNode) {
      flexAncestor.parentNode.insertBefore(counter, flexAncestor.nextSibling);
    } else {
      field.insertAdjacentElement("afterend", counter);
    }

    const stillInFlex = counter.closest(".flex-container, .field-flex");
    if (stillInFlex && stillInFlex.parentNode) {
      stillInFlex.parentNode.insertBefore(counter, stillInFlex.nextSibling);
    }

    const nowInFlex = counter.closest(".flex-container, .field-flex");
    if (nowInFlex && formRow && formRow !== nowInFlex) {
      formRow.appendChild(counter);
    }

    field.addEventListener("input", render);
    render();

    field.dataset.charcountRendered = "1";
  });
});
