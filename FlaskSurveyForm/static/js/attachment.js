console.log("Attachments script loaded");

// Initialize Dropzone
Dropzone.autoDiscover = false;

document.addEventListener("DOMContentLoaded", function () {
  const dropzone = document.getElementById("dropzone");
  if (!dropzone) return;

  const myDropzone = new Dropzone("#dropzone", {
    url: "/upload_attachment",
    paramName: "file",
    maxFilesize: 10, // MB
    acceptedFiles: ".pdf,.doc,.docx,.xls,.xlsx,.jpg,.png,.txt",
    addRemoveLinks: true,
    dictDefaultMessage: "Drop files here or click to upload",
    init: function () {
      this.on("success", function (file, response) {
        if (response.success) {
          // Add file to the table
          const tbody = document.getElementById("attachments-table-body");
          const tr = document.createElement("tr");
          tr.setAttribute("data-filename", response.filename);
          tr.innerHTML = `
                        <td>${response.filename}</td>
                        <td><input type="text" class="form-control form-control-sm" name="attachment_descriptions[]" placeholder="Add description"></td>
                        <td>
                            <button type="button" class="btn btn-sm btn-danger remove-attachment" data-filename="${response.filename}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    `;
          tbody.appendChild(tr);

          // Add hidden input for the file
          const hiddenInput = document.createElement("input");
          hiddenInput.type = "hidden";
          hiddenInput.name = "attachments[]";
          hiddenInput.value = response.filename;
          tr.appendChild(hiddenInput);
        }
      });

      this.on("removedfile", function (file) {
        // Remove file from the table
        const tr = document.querySelector(`tr[data-filename="${file.name}"]`);
        if (tr) tr.remove();
      });

      this.on("error", function (file, errorMessage) {
        if (typeof errorMessage === "string") {
          alert(errorMessage);
        } else if (errorMessage.errors) {
          alert(errorMessage.errors.join("\n"));
        }
      });
    }
  });

  // Handle removing attachments
  document.addEventListener("click", function (e) {
    if (e.target.closest(".remove-attachment")) {
      const button = e.target.closest(".remove-attachment");
      const filename = button.dataset.filename;
      const tr = button.closest("tr");

      // Remove the file from Dropzone
      const file = myDropzone
        .getAcceptedFiles()
        .find((f) => f.name === filename);
      if (file) {
        myDropzone.removeFile(file);
      }

      // Remove the row from the table
      tr.remove();
    }
  });
});
