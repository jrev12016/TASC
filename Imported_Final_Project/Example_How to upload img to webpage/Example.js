const fileInput = document.getElementById('fileInput');
const selectedImage = document.getElementById('selectedImage');
const imageContainer = document.getElementById('imageContainer');

fileInput.addEventListener('change', function () {
    const selectedFile = fileInput.files[0];

    if (selectedFile) {
        const reader = new FileReader();

        reader.onload = function (e) {
            selectedImage.src = e.target.result;
            selectedImage.style.display = 'block';
            imageContainer.style.display = 'block';
        };

        reader.readAsDataURL(selectedFile);
    }
});
