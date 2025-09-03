(function($) {
  function getCookie(name) {
    var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : '';
  }
  function adminRoot() {
    return window.location.pathname.replace(/\/\d+\/change\/?$/, '');
  }

  function attach(ctx) {
    $(ctx).find('input[type=checkbox][name$="-DELETE"]').each(function() {
      var $del = $(this);
      var $item = $del.closest('.inline-related, tr, .form-row');

      if ($item.hasClass('empty-form')) return;
      if ($item.data('instant-bound') === true) return;

      var $id = $item.find('input[type=hidden][name$="-id"]').first();
      var pk = $id.val();
      if (!pk) return;

      var cbId = $del.attr('id');
      var $label = cbId ? $item.find('label[for="'+cbId+'"]') : $();
      var $anchor = $label.length ? $label : $del;

      if ($item.find('.js-inline-delete-now').length) {
        $item.data('instant-bound', true);
        return;
      }

      var $btn = $('<button type="button" class="button js-inline-delete-now">Удалить</button>');
      $btn.on('click', function() {
        if (!confirm('Удалить этот элемент?')) return;

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
          $del.prop('checked', true).trigger('change');
          $item.addClass('inline-marked-for-delete').hide();
        })
        .catch(function(err) {
          alert('Ошибка удаления: ' + err.message);
          $btn.prop('disabled', false);
        });
      });

      $anchor.after($btn);
      if ($label.length) $label.hide();
      $del.hide();

      $item.data('instant-bound', true);
    });
  }

  $(document).ready(function(){ attach($(document)); });
  $(document).on('formset:added', function(e, $row){ attach($row); });
})(django.jQuery);
