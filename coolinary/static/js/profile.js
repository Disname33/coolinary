// Получаем элементы формы и области предпросмотра
const form = document.getElementById('avatar-form');
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const imageUpload = document.getElementById('avatar_file_upload');
const imagePreview = document.getElementById('image-preview');
const changedField = new Set();


let cropData;
let cropper;

function elementsAddEventListener(...names) {
    const namedFields = [];
    names.forEach(name => {
        namedFields.push(...document.querySelectorAll('[name=' + name + ']'))
    });
    namedFields.forEach(el => {
        el.addEventListener("change", function () {
            changedField.add(el.name)
            console.info(el)
        });
    });
}

const formElement = ['birthday', 'country', 'city', 'display_option', 'gender']
const formPassword = ['new_password1', 'new_password2', 'old_password']
const formEmail = ['email', 'old_email']
const formName = ['first_name', 'last_name']
elementsAddEventListener(...formElement, ...formPassword, ...formEmail, ...formName)


console.info("%cDisname", "border: 5px solid orange; border-radius: 50%; font-size: 40px; padding: 25px; color: white; background: red; font-weight: bold")
$(document).ready(function () {
    // Обработчик загрузки файла изображения
    imageUpload.addEventListener('change', function (event) {
        const input = $('#avatar_file_upload')[0];
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                $('#image-crop').attr('src', e.target.result);
                $('#image-crop').ready(function () {
                    showEl(imagePreview);
                    if (window.innerWidth > 770) showElByID('btn-load1');
                    showElByID('edit-img');
                    initCroper()
                });
            };
            reader.readAsDataURL(input.files[0]);
        }
    });


    function initCroper() {
        const image = document.getElementById('image-crop');
        image.scrollIntoView({behavior: "smooth", block: "center"});
        cropper = new Cropper(image, {
            aspectRatio: 1, // Соотношение сторон для области
            viewMode: 2,
            dragMode: 'move', // Режим перетаскивания
            cropBoxResizable: true, // Возможность изменения размера области
            crop: function (event) {
                cropData = cropper.getData();
                console.info(cropData);
            }
        });
    }

});

function sendAvatar() {
    showElByID("spiner")
    // Создаем новый Canvas элемент
    const imageExt = $('#avatar_file_upload')[0].files[0].name.split(".");
    const imageFormat = (imageExt.length > 1 && imageExt[imageExt.length - 1].toLowerCase() === 'png') ? 'png' : 'jpeg';
    const croppedCanvas = cropper.getCroppedCanvas({maxWidth: 800, maxHeight: 800})
    const croppedImageData = croppedCanvas.toDataURL('image/' + imageFormat);
    $.ajax({
        url: window.location.href,
        type: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'file': croppedImageData,
            'image_format': imageFormat,
        },
        success: function (response) {
            console.log(response)
            location.reload();
        },
        error: function (error) {
            console.error(error);
            alert(error.statusText)
        }
    });
}

function deleteAvatar() {
    $.ajax({
        url: window.location.href,
        type: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            'delete_avatar': "x",
        },
        success: () => location.reload(),
        error: function (error) {
            console.log(error);
            alert(error.statusText)
        }
    });
}

const opacityButtons = document.querySelectorAll(".btn-opacity");

opacityButtons.forEach(function (opacityButton) {
        opacityButton.addEventListener("mouseenter", function () {
            opacityButton.style.opacity = "1";
        });
        opacityButton.addEventListener("mouseleave", function () {
            opacityButton.style.opacity = "0.5";
        });
    }
)

function loadFileImage() {
    if (typeof cropper !== "undefined") {
        cropper.destroy();
        hideEl(imagePreview);
    }
    imageUpload.click()
}

function maximizeCrop() {
    const canvasData = cropper.getCanvasData();
    const minSize = Math.min(canvasData.width, canvasData.height)
    const left = (canvasData.width - minSize) / 2
    const top = (canvasData.height - minSize) / 2
    cropper.setCropBoxData({"left": left, "top": top, "width": minSize, "height": minSize})
}

function saveSettings() {
    if (changedField.size !== 0) {
        let request_data = {'save': "True"};
        if (changedField.has(formPassword[1])) {
            if (getValueAtName(formPassword[0]) === getValueAtName(formPassword[1])) {
                formPassword.forEach(name => {
                    request_data[name] = getValueAtName(name)
                })
            } else {
                alert("Пароли не совпадают!")
            }
        }
        if (changedField.has(formEmail[0])) {
            formEmail.forEach(name => {
                request_data[name] = getValueAtName(name)
            })
        }
        if (changedField.has(formName[0]) || changedField.has(formName[1])) {
            formName.forEach(name => {
                request_data[name] = getValueAtName(name)
            })
        }
        // {#changedField.forEach(name => {request_data[name] = getValueAtName(name)})#}
        formElement.forEach(name => {
            request_data[name] = getValueAtName(name)
        })
        $.ajax({
            url: window.location.href,
            type: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            data: request_data,
            success: function (response) {
                console.log(response)
                if (response.status === "OK") {
                    alert("Параметры обновлены")
                    location.reload();
                } else {
                    alert(response.error)
                }

            },
            error: function (error) {
                console.error(error);
                alert(error.statusText)
            }
        });
    } else {
        alert("Ни одно значение не изменено, нечего сохранять!")
    }

}

function getValueAtName(name) {
    const Elements = document.querySelectorAll('[name=' + name + ']');
    if (Elements.length === 1) {
        return Elements[0].value;
    } else {
        let radioValue = '';
        Elements.forEach(button => {
            if (button.checked) radioValue = button.value
        });
        return radioValue
    }

}
