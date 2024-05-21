document.addEventListener('DOMContentLoaded', function () {
    const imageGeneratorCheckbox = document.getElementById("imageGenerator");
    providerSelect.addEventListener("click", () => {
        imageGeneratorCheckbox.checked = false;
    })
    imageGeneratorCheckbox.addEventListener("click", async () => {
        const providerSelect = document.getElementById("provider");
        const modelSelect = document.getElementById("model");
        const model2Select = document.getElementById("model2");
        if (imageGeneratorCheckbox.checked) {
            let options = providerSelect.options;

            for (let i = 0; i < options.length; i++) {
                if (options[i].value === 'BingCreateImages') {
                    providerSelect.selectedIndex = i;
                    await load_provider_models(i)
                    break;
                }
            }

            options = modelSelect.options;

            for (let i = 0; i < options.length; i++) {
                if (options[i].value === 'gpt-4o') {
                    modelSelect.selectedIndex = i;
                    break;
                }
            }

            options = model2Select.options;

            for (let i = 0; i < options.length; i++) {
                if (options[i].value === 'gpt-4o') {
                    model2Select.selectedIndex = i;
                    break;
                }
            }


        } else {
            model2Select.classList.add("hidden");
            modelSelect.classList.remove("hidden");
            providerSelect.selectedIndex = appStorage.getItem("provider");
            modelSelect.selectedIndex = appStorage.getItem("model");
            model2Select.selectedIndex = appStorage.getItem("model2");
        }
    });
});
