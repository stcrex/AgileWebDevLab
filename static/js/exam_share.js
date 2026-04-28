(function () {
  const $panel = $("#sharePanel");
  if (!$panel.length) return;
  const examId = $panel.data("exam-id");
  if (!examId) return;

  const $active = $("#shareActive");
  const $inactive = $("#shareInactive");
  const $input = $("#shareUrlInput");
  const $err = $("#shareError");

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

  function showActive(url) {
    $input.val(url);
    $active.removeClass("d-none");
    $inactive.addClass("d-none");
  }

  function showInactive() {
    $input.val("");
    $active.addClass("d-none");
    $inactive.removeClass("d-none");
  }

  $("#btnCreateShare").on("click", function () {
    const $btn = $(this).prop("disabled", true);
    showErr("");
    $.post("/api/exams/" + examId + "/share-token")
      .done(function (res) {
        showActive(res.share_url || "");
      })
      .fail(function (xhr) {
        const msg = (xhr.responseJSON && xhr.responseJSON.error) || xhr.statusText;
        showErr(msg);
      })
      .always(function () {
        $btn.prop("disabled", false);
      });
  });

  $("#btnRevokeShare").on("click", function () {
    if (!window.confirm("Revoke this share link? It will stop working for everyone.")) return;
    const $btn = $(this).prop("disabled", true);
    showErr("");
    $.ajax({ url: "/api/exams/" + examId + "/share-token", method: "DELETE" })
      .done(function () {
        showInactive();
      })
      .fail(function (xhr) {
        const msg = (xhr.responseJSON && xhr.responseJSON.error) || xhr.statusText;
        showErr(msg);
      })
      .always(function () {
        $btn.prop("disabled", false);
      });
  });

  $("#btnCopyShare").on("click", function () {
    const v = $input.val();
    if (!v) return;
    navigator.clipboard.writeText(v).catch(function () {
      $input.select();
      document.execCommand("copy");
    });
  });
})();
