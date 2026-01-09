window.hyperdiv.registerPlugin("file_picker", (ctx) => {
  // Criamos o input de arquivo (escondido)
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = "image/*";
  fileInput.style.display = "none";

  // Criamos o botão visual
  const button = document.createElement("button");
  button.innerText = "+";
  button.title = "Selecionar imagem";
  
  // Estilização básica para combinar com o botão do Hyperdiv
  button.style.padding = "8px 16px";
  button.style.cursor = "pointer";
  button.disabled = false;

  // Ao clicar no botão, acionamos o clique do input invisível
  button.addEventListener("click", () => {
    fileInput.click();
  });

  // Quando o usuário seleciona o arquivo
  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        // Atualizamos a propriedade image_metadata do plugin
        ctx.updateProp("image_metadata", {
            name: file.name,
            content: event.target.result // Base64
        });
      };
      reader.readAsDataURL(file);
    }
  });

  ctx.onPropUpdate((propName, propValue) => {
    if (propName === "image_metadata" && propValue === null)
      fileInput.value = ""; // Reseta o input para permitir re-upload do mesmo arquivo

    if (propName === "disabled")
      button.disabled = propValue;
  });

  // Adicionamos os elementos ao Shadow DOM do plugin
  ctx.domElement.appendChild(button);
  ctx.domElement.appendChild(fileInput);
});