(function () {
  const examId = window.__EXAM_ID__;
  if (!examId) return;

  const $list = $("#resourceList");
  const $err = $("#resourceError");
  const $result = $("#resourceResult");

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
        xhr.setRequestHeader("X-CSRFToken", $('meta[name="csrf-token"]').attr("content"));
      }
    },
  });

  function showErr(msg) {
    if (!msg) {
      $err.addClass("d-none").text("");
    } else {
      $err.removeClass("d-none").text(msg);
    }
  }

  function renderRow(r) {
    const $tr = $("<tr>").attr("data-id", r.id);
    $tr.append(
      $("<td>").append(
        $("<a>", { href: r.url, target: "_blank", rel: "noopener noreferrer" }).text(r.title)
      )
    );
    $tr.append($("<td>").append($("<code>", { class: "small text-break" }).text(r.url)));
    const $actions = $("<td class=\"text-end\">");
    const $btnDel = $("<button type=\"button\" class=\"btn btn-outline-danger btn-sm\">Delete</button>");
    $btnDel.on("click", function () {
      if (!window.confirm("Remove this resource?")) return;
      $btnDel.prop("disabled", true);
      $.ajax({ url: "/api/exams/" + examId + "/resources/" + r.id, method: "DELETE" })
        .done(function () {
          $tr.remove();
          $result.text("Deleted resource #" + r.id);
        })
        .fail(function (xhr) {
          const msg = (xhr.responseJSON && xhr.responseJSON.error) || xhr.statusText;
          showErr(msg);
        })
        .always(function () {
          $btnDel.prop("disabled", false);
        });
    });
    $actions.append($btnDel);
    $tr.append($actions);
    return $tr;
  }

  function loadList() {
    showErr("");
    $.getJSON("/api/exams/" + examId + "/resources")
      .done(function (data) {
        $list.empty();
        (data.resources || []).forEach(function (r) {
          $list.append(renderRow(r));
        });
      })
      .fail(function (xhr) {
        showErr((xhr.responseJSON && xhr.responseJSON.error) || xhr.statusText);
      });
  }

  $("#formAddResource").on("submit", function (e) {
    e.preventDefault();
    const title = $("#resTitle").val().trim();
    const url = $("#resUrl").val().trim();
    showErr("");
    $.ajax({
      url: "/api/exams/" + examId + "/resources",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ title: title, url: url }),
    })
      .done(function (res) {
        $("#resTitle, #resUrl").val("");
        $list.append(renderRow(res.resource));
        $result.text("Added resource #" + res.resource.id);
      })
      .fail(function (xhr) {
        const msg = (xhr.responseJSON && xhr.responseJSON.error) || xhr.statusText;
        showErr(msg);
      });
  });

  loadList();
})();
