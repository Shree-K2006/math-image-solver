let selectedFile;

document.getElementById("imageInput").addEventListener("change", function(e) {
    selectedFile = e.target.files[0];
});

async function uploadImage() {
    if (!selectedFile) {
        alert("Please select an image first!");
        return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    const res = await fetch("http://localhost:8000/compute", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    const resultDiv = document.getElementById("result");
    if (data.error) {
        resultDiv.innerText = "Error: " + data.error;
    } else {
        resultDiv.innerText = `Expression: ${data.expression}\nResult: ${data.result}`;
    }
}