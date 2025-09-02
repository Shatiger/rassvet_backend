(function($) {
  function getCookie(name) {
    var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : '';
  }
  // /admin/app/model/123/change/ -> /admin/app/model
  function adminRoot() {
    return window.location.pathname.replace(/\/\d+\/change\/?$/, '');
  }

  function attach(ctx) {
    // Ищем чекбоксы удаления — работает и для StackedInline, и для TabularInline
    $(ctx).find('input[type=checkbox][name$="-DELETE"]').each(function() {
      var $del = $(this);
      var $item = $del.closest('.inline-related, tr, .form-row');  // контейнер блока/строки

      if ($item.hasClass('empty-form')) return;                    // шаблон новой формы
      if ($item.data('instant-bound') === true) return;            // уже обработано

      // pk из скрытого -id в этом же контейнере
      var $id = $item.find('input[type=hidden][name$="-id"]').first();
      var pk = $id.val();
      if (!pk) return;                                             // только существующие объекты

      // свяжем label по атрибуту for, чтобы корректно его скрыть
      var cbId = $del.attr('id');
      var $label = cbId ? $item.find('label[for="'+cbId+'"]') : $();
      var $anchor = $label.length ? $label : $del;

      // если кнопка уже есть — не добавляем
      if ($item.find('.js-inline-delete-now').length) {
        $item.data('instant-bound', true);
        return;
      }

      var $btn = $('<button type="button" class="button js-inline-delete-now">Удалить</button>');
      $btn.on('click', function() {
        if (!confirm('Удалить этот элемент?')) return;

        // защита от даблкликов
        if ($btn.prop('disabled')) return;
        $btn.prop('disabled', true);

        var url = adminRoot() + '/inline-delete/' + pk + '/';
        fetch(url, {
          method: 'POST',
          headers: { 'X-CSRFToken': getCookie('csrftoken') }
        })
        .then(function(r) {
          if (!r.ok) {
            return r.text().then(function(t) {
              var msg = 'HTTP ' + r.status;
              if (r.status === 403) msg += ' (нет прав или CSRF)';
              if (r.status === 404) msg += ' (не найдено)';
              throw new Error(msg + ': ' + t.slice(0, 200));
            });
          }
          var ct = r.headers.get('content-type') || '';
          if (ct.indexOf('application/json') === -1) {
            return r.text().then(function(t){ throw new Error('Unexpected content-type: ' + ct + ' ' + t.slice(0,200)); });
          }
          return r.json();
        })
        .then(function() {
          // Помечаем как удалённое штатно и скрываем элемент
          $del.prop('checked', true).trigger('change');
          $item.addClass('inline-marked-for-delete').hide();
        })
        .catch(function(err) {
          alert('Ошибка удаления: ' + err.message);
          $btn.prop('disabled', false); // даём шанс повторить
        });
      });

      // вставляем кнопку рядом с label/checkbox
      $anchor.after($btn);
      if ($label.length) $label.hide();
      $del.hide();

      // помечаем ВЕСЬ контейнер как обработанный (анти-дубль)
      $item.data('instant-bound', true);
    });
  }

  $(document).ready(function(){ attach($(document)); });
  $(document).on('formset:added', function(e, $row){ attach($row); });
})(django.jQuery);
