document.addEventListener('DOMContentLoaded', function () {

    const imageGeneratorCheckbox = document.getElementById("imageGenerator");

    imageGeneratorCheckbox.addEventListener("click", async () => {
        const providerSelect = document.getElementById("provider");
        const modelSelect = document.getElementById("model");
        const model2Select = document.getElementById("model2");
        console.info('click')
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
            providerSelect.selectedIndex = 0;
            modelSelect.selectedIndex = 0;
            model2Select.selectedIndex = 0;
        }
    });
});
